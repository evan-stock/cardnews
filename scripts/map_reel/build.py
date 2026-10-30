#!/usr/bin/env python3
"""지도 애니메이션 릴스 만들기 (오늘의쓸모, 2026.10.30 이탈리아 총파업 시안에서 만든 틀)

사용:
  python3 scripts/map_reel/build.py drafts/map_reel/<id>.json            # 미리보기 사진 몇 장 (work/<id>/shots)
  python3 scripts/map_reel/build.py drafts/map_reel/<id>.json --video    # 전체 mp4 (media/<id>/map_reel.mp4)

원고(spec) 형식은 README.md 참고. 예시: drafts/map_reel/20261030-italymap.json
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

def run(cmd, cwd=None):
    print('$', ' '.join(cmd)); subprocess.run(cmd, cwd=cwd, check=True)

def main():
    spec_path = os.path.abspath(sys.argv[1]); video = '--video' in sys.argv
    spec = json.load(open(spec_path))
    sid = spec['id']
    work = os.path.join(HERE, 'work', sid); os.makedirs(os.path.join(work, 'ph'), exist_ok=True)
    if not os.path.isdir(os.path.join(HERE, 'node_modules', 'world-atlas')):
        run(['npm', 'i', '--silent'], cwd=HERE)
    run(['node', os.path.join(HERE, 'geo.mjs'), spec_path, os.path.join(work, 'geo.json')])
    geo = json.load(open(os.path.join(work, 'geo.json')))

    # 사진 복사(저장소 기준 경로) → ph/
    def ph(p):
        if not p: return None
        src = os.path.join(ROOT, p); dst = 'ph/' + os.path.basename(p)
        shutil.copy(src, os.path.join(work, dst)); return dst

    # 시각 자동 계산: 인트로 3.3초 → 장면마다 scene_len(기본 3.3) → 정리 3.1초 → CTA 2.6초
    L = spec.get('scene_len', 3.3); intro_end = spec.get('intro_len', 3.3)
    t = intro_end + 0.3
    scenes = []
    for sc in spec['scenes']:
        sc = dict(sc); sc['t'] = round(t, 2); t += sc.get('len', L)
        if sc.get('card') and sc['card'].get('img'): sc['card'] = dict(sc['card'], img=ph(sc['card']['img']))
        for p in sc['pins']: assert p['k'] in geo['pts'], '도시 좌표 없음: ' + p['k']
        scenes.append(sc)
    recap_t = round(t, 2); cta_t = round(t + spec.get('recap_len', 3.1), 2); dur = round(cta_t + spec.get('cta_len', 2.6), 2)
    S = {
        'tag': spec['tag'], 'title': spec['title'], 'ctaText': spec['cta'],
        'intro': dict(spec['intro'], img=ph(spec['intro']['img']), end=intro_end),
        'scenes': scenes, 'recap': {'t': recap_t, 'b': spec['recap']},
        'dots': [d for d in spec.get('dots', []) if d in geo['pts']], 'cta': cta_t, 'dur': dur,
    }
    with open(os.path.join(work, 'data.js'), 'w') as f:
        f.write('window.GEO=' + json.dumps(geo) + ';\nwindow.SCENES=' + json.dumps(S, ensure_ascii=False) + ';')
    for n in ['index.html', 'render.cjs']: shutil.copy(os.path.join(HERE, n), work)
    os.makedirs(os.path.join(work, 'fonts'), exist_ok=True)
    for n in ['Pretendard-Black.otf', 'Pretendard-Medium.otf', 'Pretendard-SemiBold.otf']:
        shutil.copy(os.path.join(ROOT, 'assets', 'fonts', n), os.path.join(work, 'fonts'))
    shutil.copy(os.path.join(ROOT, 'brand', 'logo_typo_A.png'), os.path.join(work, 'logo.png'))
    print(f'길이 {dur}초 · 장면 {len(scenes)}개 · 정리 {recap_t}초 · CTA {cta_t}초')

    if not video:
        ts = [1.0] + [s['t'] + 1.6 for s in scenes] + [recap_t + 1.5, cta_t + 1.2]
        run(['node', 'render.cjs', 'shots', ','.join(f'{x:.2f}' for x in ts)], cwd=work)
        print('미리보기:', os.path.join(work, 'shots')); return
    if '--audio-only' not in sys.argv or not os.path.exists(os.path.join(work, 'frames', 'f00000.jpg')):
        shutil.rmtree(os.path.join(work, 'frames'), ignore_errors=True)
        run(['node', 'render.cjs', 'frames', '30'], cwd=work)
    out_dir = os.path.join(ROOT, 'media', sid); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'map_reel.mp4')
    bgm = spec.get('bgm')  # {"file": "assets/bgm/worthy/subway_dreams.mp3", "start": 46.0, "vol": 0.28} (assets/bgm/README.md 값)
    if bgm:
        # 배경음악: 하이라이트 구간부터, 처음 0.3초 페이드인·끝 1.5초 페이드아웃. 효과음은 sfx:true일 때만 작게 얹음
        flt = (f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,volume={bgm.get('vol', 0.4)},"
               f"afade=t=in:d=0.3,afade=t=out:st={dur - 1.5}:d=1.5[m]")
        ins = ['-ss', str(bgm.get('start', 0)), '-i', os.path.join(ROOT, bgm['file'])]
        if spec.get('sfx', False):
            sys.path.insert(0, HERE); import sfx
            sfx.make(S, os.path.join(work, 'sfx.wav'), use_bed=False)
            ins += ['-i', 'sfx.wav']; flt += ';[2:a]volume=0.45[s];[m][s]amix=inputs=2:normalize=0[a]'
        else:
            flt += ';[m]anull[a]'
        audio = ins + ['-filter_complex', flt, '-map', '0:v', '-map', '[a]']
    elif spec.get('sfx', True):
        sys.path.insert(0, HERE); import sfx
        sfx.make(S, os.path.join(work, 'sfx.wav'), use_bed=spec.get('sfx_bed', True)); audio = ['-i', 'sfx.wav']
    else:
        audio = ['-f', 'lavfi', '-t', str(dur), '-i', 'anullsrc=r=44100:cl=stereo']
    run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', 'frames/f%05d.jpg'] + audio + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-shortest', '-movflags', '+faststart', out], cwd=work)
    shutil.copy(os.path.join(work, 'frames', 'f00000.jpg'), os.path.join(out_dir, 'map_reel_cover.jpg'))
    print('완성:', out)

if __name__ == '__main__':
    main()
