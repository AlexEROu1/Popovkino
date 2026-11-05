#!/usr/bin/env python3
"""Строит ноты для гитарной мини-игры по треку.
python3 make_chart.py song.wav chart.json
Ритм — ровная сетка по найденному темпу; ноты — на долях/восьмых, где в музыке есть удар;
дорожка (0 зелёная, 1 красная, 2 синяя) — по высоте звука (ниже/выше соседних нот);
длинные ноты — где звук тянется до следующей ноты. Три набора: easy / normal / hard."""
import sys, json, numpy as np, librosa
wav, out = sys.argv[1], sys.argv[2]
y, sr = librosa.load(wav, sr=22050, mono=True); H = 256
yh, yp = librosa.effects.hpss(y)
_, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512, units='time')
# ровная сетка: прямая через найденные доли
k = np.arange(len(beats)); P, t0 = np.polyfit(k, beats, 1)
while t0 - P > 0: t0 -= P
dur = len(y) / sr
CHORUS = (37.6, 69.0)
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=H)
envh = librosa.onset.onset_strength(y=yh, sr=sr, hop_length=H)
tt = librosa.times_like(env, sr=sr, hop_length=H)
rmsh = librosa.feature.rms(y=yh, hop_length=H)[0]
cent = librosa.feature.spectral_centroid(y=yh, sr=sr, hop_length=H)[0]
chroma = librosa.feature.chroma_cqt(y=yh, sr=sr, hop_length=H)
def at(arr, t, w=.045):
    m = (tt >= t - w) & (tt <= t + w); return arr[m].max() if m.any() else 0
def mean(arr, a, b):
    m = (tt >= a) & (tt < b); return arr[m].mean() if m.any() else 0
# слоты — восьмые
slots = []
i = 0
while True:
    t = t0 + i * P / 2
    if t > dur - .6: break
    if t > .3:
        s = at(env, t) + .6 * at(envh, t)
        slots.append(dict(t=float(t), i=i, beat=i % 2 == 0, bar=i % 8 == 0, s=float(s), chorus=CHORUS[0] <= t < CHORUS[1]))
    i += 1
S = np.array([x['s'] for x in slots])
# сила относительно соседей (±4 c), чтобы и в тихом вступлении были ноты
for x in slots:
    near = [y_['s'] for y_ in slots if abs(y_['t'] - x['t']) < 4]
    x['r'] = x['s'] / (np.percentile(near, 80) + 1e-9)
def pitch(t):
    m = (tt >= t - .03) & (tt <= t + .12)
    c = chroma[:, m].mean(1) if m.any() else np.zeros(12)
    pc = int(np.argmax(c)); oct_ = at(cent, t, .06)
    return pc + 12 * np.log2(max(oct_, 60) / 440)
def build(level):
    if level == 'easy':
        pick = [x for x in slots if x['beat'] and (x['r'] > (.55 if x['chorus'] else .7) or x['bar'])]
        # не чаще раза в долю, в куплете — не чаще раза в две доли
        res = []; 
        for x in pick:
            gap = P * (1 if x['chorus'] else 2) * .95
            if not res or x['t'] - res[-1]['t'] >= gap: res.append(x)
    elif level == 'normal':
        res = [x for x in slots if (x['beat'] and (x['r'] > (.45 if x['chorus'] else .6) or x['bar'])) or (not x['beat'] and x['chorus'] and x['r'] > .95)]
    else:
        res = [x for x in slots if (x['beat'] and (x['r'] > .35 or x['bar'])) or (not x['beat'] and x['r'] > (.7 if x['chorus'] else .9))]
    res = sorted(res, key=lambda x: x['t'])
    # дорожки по высоте звука: выше предыдущей — правее, ниже — левее
    notes = []; lane = 1; prev = None
    for n, x in enumerate(res):
        p = pitch(x['t'])
        if prev is not None:
            d = p - prev
            if d > .6: lane = min(2, lane + (2 if d > 4 and lane == 0 else 1))
            elif d < -.6: lane = max(0, lane - (2 if d < -4 and lane == 2 else 1))
            elif len(notes) >= 3 and all(q[1] == lane for q in notes[-3:]): lane = (lane + 1) % 3 if lane < 2 else 1
        prev = p
        notes.append([round(x['t'], 3), lane, 0])
    # длинные ноты: дальше пусто ≥ 1.5 доли и звук держится
    for j in range(len(notes) - 1):
        t, ln, _ = notes[j]; gap = notes[j + 1][0] - t
        if gap >= P * 1.45:
            sustain = mean(rmsh, t + .1, t + gap - .1) / (at(rmsh, t, .05) + 1e-9)
            if sustain > .55:
                notes[j][2] = round(min(gap - P * .5, P * 3), 3)
    # аккорды на «Сложно»: в припеве на сильную долю каждого второго такта — две кнопки
    if level == 'hard':
        extra = []
        for x in slots:
            if x['chorus'] and x['i'] % 16 == 0:
                for nt in notes:
                    if abs(nt[0] - x['t']) < .01 and nt[2] == 0:
                        extra.append([nt[0], 1 if nt[1] != 1 else 2, 0])
        notes = sorted(notes + extra)
    return notes
chart = dict(bpm=round(60 / P, 2), offset=round(float(t0), 3), duration=round(dur, 2), chorus=list(CHORUS),
             easy=build('easy'), normal=build('normal'), hard=build('hard'))
json.dump(chart, open(out, 'w'))
for lv in ('easy', 'normal', 'hard'):
    n = chart[lv]; holds = sum(1 for x in n if x[2] > 0); lanes = np.bincount([x[1] for x in n], minlength=3)
    print(lv, 'нот', len(n), 'длинных', holds, 'по дорожкам', lanes.tolist(), 'нот/с в куплете',
          round(sum(1 for x in n if x[0] < 35) / 35, 2), 'в припеве', round(sum(1 for x in n if 37.6 <= x[0] < 69) / 31.4, 2))
print('bpm', chart['bpm'], 'offset', chart['offset'])
