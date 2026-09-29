"""Knob-typing simulator + Bayesian lexicon decoder.

Model
-----
Travel is 26 "letter widths" (A..Z). A user turns to where they believe each
letter is and pauses; the pause centroid is an observation o_t.
  o = 13 + s*(mu - 13) + b + N(0, sigma_i)     (per-user bias b, scale drift s)
Segmentation errors: dropped pauses, spurious hesitation pauses, two close
letters merging into one (long) pause. Double letters ("ll") are ONE pause with
a *long-dwell* flag (the convention); the segmenter detects it imperfectly.

Decoder: for every lexicon word, Viterbi alignment (edit-distance DP with
match / delete / insert) of the observation sequence against the word's letter
positions, emission = Gaussian log-lik + long-flag log-lik, plus log P(word).
"""
import json, math, sys, time
import numpy as np
from wordfreq import top_n_list, word_frequency

rng = np.random.default_rng(7)
ALPHA = "abcdefghijklmnopqrstuvwxyz"
IDX = {c: i for i, c in enumerate(ALPHA)}

# ---------------------------------------------------------------- layouts
LETTER_FREQ = {  # English letter frequency (%), standard table
    'e':12.7,'t':9.1,'a':8.2,'o':7.5,'i':7.0,'n':6.7,'s':6.3,'h':6.1,'r':6.0,'d':4.3,
    'l':4.0,'c':2.8,'u':2.8,'m':2.4,'w':2.4,'f':2.2,'g':2.0,'y':2.0,'p':1.9,'b':1.5,
    'v':1.0,'k':0.8,'j':0.15,'x':0.15,'q':0.1,'z':0.07}

def layout(name):
    """Return (centers[26], sigma_factor[26]) in letter-width units, travel 0..26."""
    if name in ("uniform", "hints"):
        w = np.ones(26)
    elif name == "freq":
        w = np.array([LETTER_FREQ[c] for c in ALPHA]) ** 0.5
        w = w / w.sum() * 26
    else:
        raise ValueError(name)
    edges = np.concatenate([[0], np.cumsum(w)])
    centers = (edges[:-1] + edges[1:]) / 2
    fac = np.ones(26)
    if name == "hints":
        # tactile hint detents on A F K P U Z (every 5 letters) + hard end stops.
        # Assumption: error grows with distance (in letters) from the nearest
        # landmark; on a landmark the user lands at 35 % of free-field sigma.
        hints = np.array([0, 5, 10, 15, 20, 25]) + 0.5
        d = np.min(np.abs(centers[:, None] - hints[None, :]), axis=1)  # 0..2
        fac = 0.35 + 0.65 * d / 2.0
    return centers, fac

# ---------------------------------------------------------------- lexicons
def collapse(word):
    """'hello' -> [(h,0),(e,0),(l,1),(o,0)]  (runs of a letter -> one unit + double flag)."""
    out = []
    for c in word:
        if out and out[-1][0] == c:
            out[-1] = (c, 1)
        else:
            out.append((c, 0))
    return out

APPS = """spotify messages calendar maps weather camera notes reminders music phone
mail slack uber timer alarm clock photos settings youtube podcasts""".split()

COMMANDS = """call text send reply read open close start stop pause play resume skip next
previous back again cancel undo redo yes no okay confirm delete save share record
remind remember note search find ask answer translate summarize explain repeat louder
quieter volume mute unmute silence brightness battery status time date today tomorrow
tonight morning evening week month year hour minute second set timer alarm snooze
wake sleep home work school gym lunch dinner coffee meeting class exam homework
email message chat group mom dad friend team boss navigate directions walk drive bus
train uber taxi weather rain temperature traffic news music song podcast playlist
shuffle like dislike bookmark list todo task done finish later soon now help
settings wifi bluetooth pair connect disconnect update check notify quiet focus
emergency location share photo video camera flash light dark mode language english
french chinese spanish lock unlock find where when who what how why left right up
down more less""".split()
NUM_WORDS = """zero one two three four five six seven eight nine ten eleven twelve thirteen
fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty
seventy eighty ninety hundred""".split()
UNITS = "seconds minutes hours days weeks percent degrees dollars".split()

def number_words(n):
    ones = NUM_WORDS[:20]; tens = {2:"twenty",3:"thirty",4:"forty",5:"fifty",6:"sixty",7:"seventy",8:"eighty",9:"ninety"}
    if n < 20: return [ones[n]]
    if n == 100: return ["hundred"]  # "one hundred" also acceptable; keep short form
    t, o = divmod(n, 10)
    return [tens[t]] + ([ones[o]] if o else [])

def make_lexicon(kind):
    if kind == "apps":
        words = APPS; p = np.ones(len(words))
    elif kind == "commands":
        words = sorted(set(COMMANDS + NUM_WORDS + UNITS + APPS)); p = np.ones(len(words))
    else:
        n = {"5k": 5000, "20k": 20000}[kind]
        words, p, seen = [], [], set()
        for w in top_n_list("en", int(n * 1.6)):
            if w.isalpha() and w.isascii() and w not in seen:
                seen.add(w); words.append(w.lower()); p.append(word_frequency(w, "en"))
            if len(words) == n: break
        p = np.array(p)
    p = p / p.sum()
    return list(words), p

class Lex:
    """Lexicon grouped by collapsed length for vectorized DP."""
    def __init__(self, words, prior, centers):
        self.words, self.prior = words, prior
        self.logp = np.log(prior)
        self.units = [collapse(w) for w in words]
        self.groups = {}
        by_len = {}
        for i, u in enumerate(self.units):
            by_len.setdefault(len(u), []).append(i)
        for L, ids in by_len.items():
            ids = np.array(ids)
            letters = np.array([[IDX[c] for c, _ in self.units[i]] for i in ids])
            dbl = np.array([[d for _, d in self.units[i]] for i in ids])
            self.groups[L] = (ids, letters, dbl)

# ---------------------------------------------------------------- noise / user
class User:
    def __init__(self, sigma, rng, bias_sd=0.6, scale_sd=0.06):
        self.sigma = sigma
        self.b = rng.normal(0, bias_sd)
        self.s = rng.normal(1, scale_sd)

SEG = dict(p_drop=0.03, p_ins=0.03, p_close_merge=0.25, close=1.0,
           p_long_dbl=0.90, p_long_single=0.05)

def observe(word, user, centers, fac, rng, seg=SEG):
    """Return obs positions, long flags, and source unit index (-1 = spurious)."""
    units = collapse(word)
    obs, flag, src = [], [], []
    prev_mu = None
    for k, (c, dbl) in enumerate(units):
        mu = centers[IDX[c]]
        if prev_mu is not None and abs(mu - prev_mu) < seg["close"] and obs and rng.random() < seg["p_close_merge"]:
            flag[-1] = 1; prev_mu = mu; continue           # merged into previous pause (looks long)
        if rng.random() < seg["p_drop"]:
            prev_mu = mu; continue                         # moved through without a pause
        o = 13 + user.s * (mu - 13) + user.b + rng.normal(0, user.sigma * fac[IDX[c]])
        obs.append(min(max(o, 0.0), 26.0))
        flag.append(1 if (dbl and rng.random() < seg["p_long_dbl"]) or (not dbl and rng.random() < seg["p_long_single"]) else 0)
        src.append(k)
        if k < len(units) - 1 and rng.random() < seg["p_ins"]:  # hesitation on the way
            nxt = centers[IDX[units[k + 1][0]]]
            obs.append(float(rng.uniform(min(mu, nxt), max(mu, nxt)))); flag.append(0); src.append(-1)
        prev_mu = mu
    if not obs:  # always at least one pause
        c = units[0][0]; obs.append(float(centers[IDX[c]])); flag.append(0); src.append(0)
    return np.array(obs), np.array(flag), src

# ---------------------------------------------------------------- decoder
class Decoder:
    def __init__(self, lex, centers, fac, sigma, b=0.0, s=1.0, lam=1.0,
                 p_del=0.05, p_ins=0.04, p_long_dbl=0.85, p_long_single=0.10, max_len_gap=3):
        self.lex, self.lam = lex, lam
        mu = 13 + s * (centers - 13) + b
        self.mu, self.sd = mu, np.maximum(sigma * fac, 0.15)
        self.lpd, self.lpi = math.log(p_del), math.log(p_ins) + math.log(1 / 26)
        self.lmatch = math.log(1 - p_del - p_ins)
        self.lf = {(1, 1): math.log(p_long_dbl), (0, 1): math.log(1 - p_long_dbl),
                   (1, 0): math.log(p_long_single), (0, 0): math.log(1 - p_long_single)}
        self.gap = max_len_gap

    def scores(self, obs, flag):
        T = len(obs)
        # letter emission table [T, 26]
        E = -0.5 * ((obs[:, None] - self.mu[None, :]) / self.sd[None, :]) ** 2 - np.log(self.sd)[None, :] - 0.9189
        E = np.maximum(E, -30.0)  # robustness cap (heavy tail)
        fl = flag.astype(bool)
        Fd = np.where(fl, self.lf[(1, 1)], self.lf[(0, 1)])   # [T] if unit is double
        Fs = np.where(fl, self.lf[(1, 0)], self.lf[(0, 0)])
        Fins = Fs  # spurious pause: treat like single
        out = np.full(len(self.lex.words), -np.inf)
        for L, (ids, letters, dbl) in self.lex.groups.items():
            if abs(L - T) > self.gap: continue
            n = len(ids)
            D = np.full((T + 1, L + 1, n), -np.inf)
            D[0, 0] = 0.0
            for j in range(1, L + 1): D[0, j] = D[0, j - 1] + self.lpd
            for t in range(1, T + 1):
                D[t, 0] = D[t - 1, 0] + self.lpi + Fins[t - 1]
                for j in range(1, L + 1):
                    em = E[t - 1, letters[:, j - 1]] + np.where(dbl[:, j - 1] == 1, Fd[t - 1], Fs[t - 1]) + self.lmatch
                    D[t, j] = np.maximum(np.maximum(D[t - 1, j - 1] + em, D[t, j - 1] + self.lpd),
                                         D[t - 1, j] + self.lpi + Fins[t - 1])
            out[ids] = D[T, L]
        return out + self.lam * self.lex.logp

def fit_user(pairs, centers, fac, floor=0.15):
    """Least squares o = a + c*mu, sigma from factor-normalised residuals."""
    mu = np.array([centers[i] for i, _ in pairs]); o = np.array([x for _, x in pairs])
    f = np.array([fac[i] for i, _ in pairs])
    A = np.stack([np.ones_like(mu), mu - 13], 1)
    (a, c), *_ = np.linalg.lstsq(A, o - 13, rcond=None)
    r = (o - 13 - a - c * (mu - 13)) / f
    return a, c, max(float(np.sqrt(np.mean(r ** 2))), floor)

# ---------------------------------------------------------------- T9 baseline
T9 = {c: k for k, s in zip("23456789", ["abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"]) for c in s}

def t9_accuracy(words, prior):
    """Perfect key presses, frequency-ranked disambiguation; token-weighted."""
    groups = {}
    for w, p in zip(words, prior):
        groups.setdefault("".join(T9[c] for c in w), []).append(p)
    top1 = top3 = 0.0
    for ps in groups.values():
        ps = sorted(ps, reverse=True)
        top1 += ps[0]; top3 += sum(ps[:3])
    uni1 = sum(1 for g in groups.values()) / len(words)
    uni3 = sum(min(3, len(g)) for g in groups.values()) / len(words)
    return top1, top3, uni1, uni3

# ---------------------------------------------------------------- experiment
def run(kind, layout_name, sigmas, n_trials, n_users=12, n_cal=20, weighting="token"):
    words, prior = make_lexicon(kind)
    centers, fac = layout(layout_name)
    lex = Lex(words, prior, centers)
    samp_p = prior if weighting == "token" else np.ones(len(words)) / len(words)
    res = {}
    for sigma in sigmas:
        c = {"gen1": 0, "gen3": 0, "per1": 0, "per3": 0, "n": 0}
        pop_sd = math.sqrt(sigma ** 2 + 0.6 ** 2 + (0.06 * 7.5) ** 2)  # population-calibrated
        for u in range(n_users):
            user = User(sigma, rng)
            # personalization: N calibration words with known targets
            pairs = []
            for w in rng.choice(len(words), n_cal, p=samp_p):
                o, f, src = observe(words[w], user, centers, fac, rng)
                un = collapse(words[w])
                pairs += [(IDX[un[k][0]], o[i]) for i, k in enumerate(src) if k >= 0]
            a, cc, sd_hat = fit_user(pairs, centers, fac)
            gen = Decoder(lex, centers, np.ones(26) * 0 + 1, pop_sd) if layout_name != "hints" else \
                  Decoder(lex, centers, np.sqrt(fac ** 2 * sigma ** 2 + 0.6 ** 2 + 0.2) / pop_sd, pop_sd)
            per = Decoder(lex, centers, fac, sd_hat, b=a, s=cc)
            for w in rng.choice(len(words), n_trials // n_users, p=samp_p):
                o, f, _ = observe(words[w], user, centers, fac, rng)
                for tag, dec in (("gen", gen), ("per", per)):
                    sc = dec.scores(o, f)
                    top = np.argpartition(-sc, 3)[:3] if len(sc) > 3 else np.arange(len(sc))
                    top = top[np.argsort(-sc[top])]
                    # ties with identical spelling impossible; compare word ids
                    c[tag + "1"] += int(top[0] == w); c[tag + "3"] += int(w in top[:3])
                c["n"] += 1
        res[sigma] = {k: (v / c["n"] if k != "n" else v) for k, v in c.items()}
        print(f"{kind:9s} {layout_name:8s} {weighting:5s} σ={sigma:<4} generic top1 {res[sigma]['gen1']:.3f} top3 {res[sigma]['gen3']:.3f} | personal top1 {res[sigma]['per1']:.3f} top3 {res[sigma]['per3']:.3f}  (n={c['n']})", flush=True)
    return res

def run_phrases(layout_name, sigmas, n_trials=300, n_users=10):
    """'<number 0-100> <unit>' typed as 1-3 knob words (press between words); grammar decode over 808 phrases."""
    vocab = sorted(set(NUM_WORDS + UNITS))
    centers, fac = layout(layout_name)
    lex = Lex(vocab, np.ones(len(vocab)) / len(vocab), centers)
    vi = {w: i for i, w in enumerate(vocab)}
    phrases = [(n, u) for n in range(101) for u in UNITS]
    res = {}
    for sigma in sigmas:
        ok1 = ok3 = tot = 0
        for _ in range(n_users):
            user = User(sigma, rng)
            pairs = []
            for w in rng.choice(len(vocab), 20):
                o, f, src = observe(vocab[w], user, centers, fac, rng); un = collapse(vocab[w])
                pairs += [(IDX[un[k][0]], o[i]) for i, k in enumerate(src) if k >= 0]
            a, cc, sd_hat = fit_user(pairs, centers, fac)
            dec = Decoder(lex, centers, fac, sd_hat, b=a, s=cc, lam=0.0)
            for _ in range(n_trials // n_users):
                n, u = phrases[rng.integers(len(phrases))]
                segs = number_words(n) + [u]
                seg_scores = [dec.scores(*observe(w, user, centers, fac, rng)[:2]) for w in segs]
                best = []
                for (n2, u2) in phrases:
                    s2 = number_words(n2) + [u2]
                    if len(s2) != len(segs): continue
                    best.append((sum(seg_scores[i][vi[x]] for i, x in enumerate(s2)), (n2, u2)))
                best.sort(reverse=True)
                ok1 += best[0][1] == (n, u); ok3 += (n, u) in [b for _, b in best[:3]]; tot += 1
        res[sigma] = {"per1": ok1 / tot, "per3": ok3 / tot, "n": tot}
        print(f"numbers+units layout={layout_name} σ={sigma}: personal top1 {ok1/tot:.3f} top3 {ok3/tot:.3f} (n={tot})", flush=True)
    return res

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    SIG = [0.3, 0.5, 0.75, 1.0, 1.5, 2.0]
    out = {}
    t0 = time.time()
    if which in ("t9", "all"):
        for kind in ("apps", "commands", "5k", "20k"):
            w, p = make_lexicon(kind)
            out[f"t9/{kind}"] = t9_accuracy(w, p)
            print("T9", kind, "token top1/top3, type top1/top3:", [round(x, 3) for x in out[f"t9/{kind}"]])
    if which in ("small", "all"):
        for lay in ("uniform", "freq", "hints"):
            out[f"apps/{lay}"] = run("apps", lay, SIG, 2400)
            out[f"commands/{lay}"] = run("commands", lay, SIG, 2400)
            out[f"phrases/{lay}"] = run_phrases(lay, SIG, n_trials=600)
    if which in ("big", "all"):
        for lay in ("uniform", "freq", "hints"):
            out[f"5k/{lay}"] = run("5k", lay, SIG, 1800)
        for lay in ("uniform", "hints"):
            out[f"20k/{lay}"] = run("20k", lay, SIG, 1500)
            out[f"20k-type/{lay}"] = run("20k", lay, [0.3, 0.5, 0.75, 1.0], 1200, weighting="type")
    json.dump({k: v for k, v in out.items()}, open(f"results_{which}.json", "w"), indent=1, default=str)
    print("done in", round(time.time() - t0), "s")
