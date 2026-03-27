#!/usr/bin/env python3
import os
import json
import csv
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def run_git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(
        ['git', *args],
        cwd=str(cwd),
        stderr=subprocess.STDOUT,
    ).decode('utf-8', errors='replace')


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def text_stats(text: str) -> dict:
    words = [w for w in text.replace('\n', ' ').split() if w.strip()]
    headings = sum(1 for line in text.split('\n') if line.lstrip().startswith('#'))
    images = text.count('![')
    links = text.count('](')
    code_fences = text.count('```')
    return {
        'chars': len(text),
        'words': len(words),
        'headings': headings,
        'images': images,
        'links': links,
        'code_fences': code_fences,
    }


def is_text_file(path: Path, sample_size: int = 2048) -> bool:
    try:
        with path.open('rb') as f:
            data = f.read(sample_size)
        if b'\x00' in data:
            return False
        try:
            data.decode('utf-8')
            return True
        except Exception:
            return False
    except Exception:
        return False


def build_tree(root: Path, exclude_dirs: set[str] | None = None) -> str:
    exclude_dirs = exclude_dirs or set()
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in exclude_dirs]
        rel = Path(dirpath).relative_to(root)
        indent = '  ' * (0 if rel == Path('.') else len(rel.parts))
        for d in dirnames:
            lines.append(f"{indent}{d}/")
        for f in sorted(filenames):
            if rel == Path('.') and f.startswith('.') and 'github' not in f:
                continue
            lines.append(f"{indent}{f}")
    return '\n'.join(lines)


def analyze_commits(root: Path) -> dict:
    try:
        count = int(run_git(['rev-list', '--count', 'HEAD'], cwd=root).strip())
    except Exception:
        count = 0

    try:
        log = run_git(['log', '--pretty=format:%H|%h|%P|%an|%ad|%s', '--date=iso'], cwd=root).strip().split('\n')
    except subprocess.CalledProcessError:
        return {
            'count': count,
            'items': [],
            'avg_msg_len': 0,
            'quality': 0.0,
            'merge_commit_count': 0,
        }

    commits = []
    quality_scores = []
    merge_commit_count = 0
    for line in log:
        if not line.strip():
            continue
        parts = line.split('|', 5)
        if len(parts) < 6:
            continue
        full_hash, short, parents, author, date, msg = parts
        msg_len = len(msg.strip())
        msg_lower = msg.strip().lower()
        generic = any(g in msg_lower for g in ['update', 'actualiza', 'fix', 'arreglo', 'cambios', 'misc', 'wip'])
        imperative = any(
            msg_lower.startswith(p)
            for p in ['add', 'create', 'anade', 'agrega', 'implement', 'refactor', 'remove', 'elimina', 'document', 'docs', 'feat', 'fix', 'chore', 'merge', 'rebase', 'resuelve']
        )
        score = 0
        if msg_len >= 12:
            score += 0.4
        if not generic:
            score += 0.3
        if imperative:
            score += 0.3
        parent_list = [p for p in parents.split() if p.strip()]
        if len(parent_list) >= 2:
            merge_commit_count += 1
        quality_scores.append(score)
        commits.append({
            'full': full_hash,
            'short': short,
            'parents': parent_list,
            'author': author,
            'date': date,
            'message': msg,
            'score': round(score, 2),
        })

    avg_len = sum(len(c['message']) for c in commits) / len(commits) if commits else 0
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    return {
        'count': max(count, len(commits)),
        'items': commits,
        'avg_msg_len': round(avg_len, 1),
        'quality': round(avg_quality, 2),
        'merge_commit_count': merge_commit_count,
    }


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(p in text for p in patterns)


def analyze_reset_activity(root: Path) -> dict:
    cp1_path = root / 'cp1-historial-inicial.txt'
    cp2_path = root / 'cp2-soft-reset.txt'
    cp3_path = root / 'cp3-mixed-reset.txt'
    cp4_path = root / 'cp4-hard-reset.txt'
    cp5_path = root / 'cp5-reset-head.txt'
    progreso_path = root / 'progreso.txt'

    cp1 = safe_read_text(cp1_path).lower()
    cp2 = safe_read_text(cp2_path).lower()
    cp3 = safe_read_text(cp3_path).lower()
    cp4 = safe_read_text(cp4_path).lower()
    cp5 = safe_read_text(cp5_path).lower()
    progreso = safe_read_text(progreso_path).lower()

    cp1_historial_ok = contains_any(cp1, ['git log --oneline', 'paso 1', 'paso 2', 'fix cosas', 'paso 4'])

    cp2_soft_status_ok = contains_any(cp2, ['git status', 'staged', 'changes to be committed'])
    cp2_soft_log_ok = contains_any(cp2, ['git log --oneline', 'paso 4'])
    cp2_soft_explain_ok = contains_any(cp2, ['soft', 'staging', 'head']) and contains_any(cp2, ['no toca', 'working directory', 'conserva'])

    cp3_mixed_status_ok = contains_any(cp3, ['git status', 'unstaged', 'changes not staged'])
    cp3_mixed_explain_ok = contains_any(cp3, ['mixed', 'soft']) and contains_any(cp3, ['staging', 'working directory'])
    cp3_history_explain_ok = contains_any(cp3, ['desaparec', 'historial', 'reset'])

    cp4_hard_effect_ok = contains_any(cp4, ['staged', 'unstaged', 'descart'])
    cp4_hard_nuclear_ok = contains_any(cp4, ['opción nuclear', 'opcion nuclear', 'peligros', 'pierde cambios'])
    cp4_progreso_ok = contains_any(cp4, ['progreso.txt', 'paso'])

    cp5_reset_head_ok = contains_any(cp5, ['git reset head progreso.txt', 'deshacer el add', 'staged', 'unstaged'])
    cp5_status_before_after_ok = contains_any(cp5, ['antes', 'después', 'despues', 'git status'])

    progreso_min_content_ok = contains_any(progreso, ['paso']) and contains_any(progreso, ['proyecto'])

    return {
        'cp1_historial_inicial': {
            'ok': cp1_historial_ok,
            'source': 'cp1-historial-inicial.txt' if cp1_path.exists() else 'missing',
        },
        'cp2_soft_reset': {
            'ok': cp2_soft_status_ok and cp2_soft_log_ok and cp2_soft_explain_ok,
            'source': 'cp2-soft-reset.txt' if cp2_path.exists() else 'missing',
        },
        'cp3_mixed_reset': {
            'ok': cp3_mixed_status_ok and cp3_mixed_explain_ok and cp3_history_explain_ok,
            'source': 'cp3-mixed-reset.txt' if cp3_path.exists() else 'missing',
        },
        'cp4_hard_reset': {
            'ok': cp4_hard_effect_ok and cp4_hard_nuclear_ok and cp4_progreso_ok,
            'source': 'cp4-hard-reset.txt' if cp4_path.exists() else 'missing',
        },
        'cp5_reset_head': {
            'ok': cp5_reset_head_ok and cp5_status_before_after_ok,
            'source': 'cp5-reset-head.txt' if cp5_path.exists() else 'missing',
        },
        'progreso_final': {
            'exists': progreso_path.exists(),
            'minimum_content_ok': progreso_min_content_ok,
        },
    }


def analyze_files(root: Path, exclude_dirs: set[str] | None = None) -> dict:
    exclude_dirs = exclude_dirs or set()
    large = []
    binaries = []
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for f in filenames:
            p = Path(dirpath) / f
            rel = p.relative_to(root)
            total_files += 1
            try:
                size = p.stat().st_size
            except Exception:
                size = 0
            if size >= 10 * 1024 * 1024:
                large.append({'path': str(rel), 'size': size})
            if not is_text_file(p):
                binaries.append(str(rel))
    return {'total_files': total_files, 'large_files': large, 'binary_files': binaries}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', required=True)
    ap.add_argument('--required', default='progreso.txt,cp1-historial-inicial.txt,cp2-soft-reset.txt,cp3-mixed-reset.txt,cp4-hard-reset.txt,cp5-reset-head.txt,reflexion-6-8.md')
    ap.add_argument('--min-commits', default='6')
    ap.add_argument('--outdir', default='reportes')
    args = ap.parse_args()

    root = Path(args.repo_root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    required = [x.strip() for x in args.required.split(',') if x.strip()]
    try:
        min_commits = int(str(args.min_commits))
    except Exception:
        min_commits = 6

    try:
        default_branch = run_git(['symbolic-ref', '--short', 'refs/remotes/origin/HEAD'], cwd=root).strip().split('/', 1)[-1]
    except Exception:
        try:
            default_branch = run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=root).strip()
        except Exception:
            default_branch = '(unknown)'

    commits_info = analyze_commits(root)
    reset_info = analyze_reset_activity(root)
    missing = [f for f in required if not (root / f).exists()]

    readme_path = root / 'README.md'
    readme_text = safe_read_text(readme_path) if readme_path.exists() else ''
    readme_stats = text_stats(readme_text) if readme_text else {'chars': 0, 'words': 0, 'headings': 0, 'images': 0, 'links': 0, 'code_fences': 0}

    reflex_path = root / 'reflexion-6-8.md'
    reflex_text = safe_read_text(reflex_path) if reflex_path.exists() else ''
    reflex_stats = text_stats(reflex_text) if reflex_text else {'words': 0}
    reflex_ok = bool(reflex_text) and reflex_stats['words'] >= 80

    evidencia_candidates = [
        'cp1', 'cp2', 'cp3', 'cp4', 'cp5',
        'reset', 'soft', 'mixed', 'hard', 'head', 'revert', 'reflexion',
    ]
    evidencias_presentes = []
    for cand in evidencia_candidates:
        for p in root.rglob(f'*{cand}*'):
            if outdir.name in p.parts or '.git' in p.parts:
                continue
            if p.is_file() and p.suffix.lower() in ('.md', '.png', '.jpg', '.jpeg', '.txt', ''):
                evidencias_presentes.append(str(p.relative_to(root)))
    evidencias_unicas = sorted(set(evidencias_presentes))
    evidencias_ok = len(evidencias_unicas) >= 6

    excluded_dirs = {'.git', outdir.name}
    files_info = analyze_files(root, exclude_dirs=excluded_dirs)
    arbol = build_tree(root, exclude_dirs=excluded_dirs)
    (outdir / 'arbol.txt').write_text(arbol, encoding='utf-8')

    s_estructura = 2
    if files_info['large_files']:
        s_estructura = 1
    if missing:
        s_estructura = 0

    checks_reset = [
        reset_info['cp1_historial_inicial']['ok'],
        reset_info['cp2_soft_reset']['ok'],
        reset_info['cp3_mixed_reset']['ok'],
        reset_info['cp4_hard_reset']['ok'],
        reset_info['cp5_reset_head']['ok'],
        reset_info['progreso_final']['exists'] and reset_info['progreso_final']['minimum_content_ok'],
    ]
    tech_hits = sum(1 for x in checks_reset if x)

    if tech_hits >= 6:
        s_git_reset = 4
    elif tech_hits >= 5:
        s_git_reset = 3
    elif tech_hits >= 4:
        s_git_reset = 2
    elif tech_hits >= 3:
        s_git_reset = 1
    else:
        s_git_reset = 0

    if evidencias_ok:
        s_evid = 3
    elif len(evidencias_unicas) >= 4:
        s_evid = 2
    elif evidencias_unicas:
        s_evid = 1
    else:
        s_evid = 0

    if reflex_ok:
        s_reflex = 3
    elif reflex_path.exists() and reflex_stats['words'] > 0:
        s_reflex = 1
    else:
        s_reflex = 0

    total = s_git_reset + s_evid + s_reflex

    resumen = {
        'repo_default_branch': default_branch,
        'required_files': required,
        'missing_required': missing,
        'commits': commits_info,
        'reset_checks': reset_info,
        'readme_stats': readme_stats,
        'reflexion_stats': reflex_stats,
        'evidencias_encontradas': evidencias_unicas,
        'files_info': files_info,
        'checks_no_puntuables': {
            'estructura': {
                'score_referencia': s_estructura,
                'max_referencia': 2,
                'estado': 'ok' if s_estructura == 2 else ('parcial' if s_estructura == 1 else 'ko'),
            },
            'min_commits': {
                'esperado': min_commits,
                'detectado': commits_info['count'],
                'ok': commits_info['count'] >= min_commits,
            },
        },
        'scores': {
            'git_reset (max_4)': s_git_reset,
            'evidencias (max_3)': s_evid,
            'reflexion (max_3)': s_reflex,
            'total': total,
            'sobre': 10,
        },
    }

    with (outdir / 'informe.json').open('w', encoding='utf-8') as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    with (outdir / 'metricas.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['criterio', 'puntuacion'])
        w.writerow(['git_reset (max 4)', s_git_reset])
        w.writerow(['evidencias (max 3)', s_evid])
        w.writerow(['reflexion (max 3)', s_reflex])
        w.writerow(['total', total])

    def badge(score: int) -> str:
        color = 'red'
        if score >= 9:
            color = 'brightgreen'
        elif score >= 7:
            color = 'green'
        elif score >= 5:
            color = 'yellow'
        elif score >= 3:
            color = 'orange'
        return f"![score](https://img.shields.io/badge/nota-{score}%2F10-{color})"

    md = []
    md.append(f"# Informe de evaluacion - {datetime.utcnow().isoformat(timespec='seconds')}Z")
    md.append(badge(total) + '')
    md.append(f"**Rama por defecto:** `{default_branch}`  ")
    md.append(f"**Minimo de commits esperado:** {min_commits}  ")
    md.append('')

    md.append('## Resultado por criterios')
    md.append('| Criterio | Puntuacion |')
    md.append('|---|---:|')
    md.append(f"| Uso de git reset (--soft, mixed, --hard, reset HEAD) | {s_git_reset}/4 |")
    md.append(f"| Evidencias (checkpoints + archivos) | {s_evid}/3 |")
    md.append(f"| Reflexion 6.8 | {s_reflex}/3 |")
    md.append(f"| **Total** | **{total}/10** |")
    md.append('')

    md.append('## Validaciones adicionales (no puntuan)')
    if s_estructura == 2:
        md.append('- Estructura del repositorio: OK')
    elif s_estructura == 1:
        md.append('- Estructura del repositorio: Parcial (hay archivos grandes)')
    else:
        md.append('- Estructura del repositorio: KO (faltan archivos obligatorios)')
    md.append(f"- Minimo de commits: {'OK' if commits_info['count'] >= min_commits else 'KO'} ({commits_info['count']}/{min_commits})")
    md.append('')

    if missing:
        md.append('> WARNING: Faltan archivos obligatorios: ' + ', '.join(missing))
        md.append('')

    md.append('## Archivos obligatorios')
    md.append(f"Requeridos: {', '.join(required)}  ")
    if missing:
        md.append(f"Faltantes: {', '.join(missing)}  ")
    else:
        md.append('Todos presentes.  ')
    md.append('')

    md.append('## Commits')
    md.append(f"- Numero de commits: **{commits_info['count']}**  ")
    md.append(f"- Calidad media de mensajes: **{commits_info['quality']}**  ")
    md.append(f"- Longitud media del mensaje: **{commits_info['avg_msg_len']}**  ")
    md.append(f"- Merge commits detectados (informativo): **{commits_info['merge_commit_count']}**  ")
    md.append('')
    md.append('<details><summary>Ver listado</summary>')
    md.append('')
    for c in commits_info['items'][:50]:
        parents_note = ' merge' if len(c['parents']) >= 2 else ''
        md.append(f"- `{c['short']}` {c['date']} - {c['message']} (score {c['score']}){parents_note}")
    md.append('</details>')
    md.append('')

    md.append('## Checks de reset')
    md.append(f"- Historial inicial (cp1): {'si' if reset_info['cp1_historial_inicial']['ok'] else 'no'}  ")
    md.append(f"- Evidencia de reset --soft (cp2): {'si' if reset_info['cp2_soft_reset']['ok'] else 'no'}  ")
    md.append(f"- Evidencia de reset mixed (cp3): {'si' if reset_info['cp3_mixed_reset']['ok'] else 'no'}  ")
    md.append(f"- Evidencia de reset --hard (cp4): {'si' if reset_info['cp4_hard_reset']['ok'] else 'no'}  ")
    md.append(f"- Evidencia de reset HEAD archivo (cp5): {'si' if reset_info['cp5_reset_head']['ok'] else 'no'}  ")
    md.append(f"- progreso.txt final presente y minimo valido: {'si' if reset_info['progreso_final']['exists'] and reset_info['progreso_final']['minimum_content_ok'] else 'no'}  ")
    md.append('')

    md.append('## Metricas del README')
    md.append(f"- Palabras: {readme_stats.get('words', 0)}  ")
    md.append(f"- Encabezados: {readme_stats.get('headings', 0)}  ")
    md.append(f"- Imagenes: {readme_stats.get('images', 0)}  ")
    md.append(f"- Enlaces: {readme_stats.get('links', 0)}  ")
    md.append('')

    md.append('## Evidencias detectadas (heuristica)')
    if evidencias_unicas:
        for evidencia in evidencias_unicas[:50]:
            md.append(f"- {evidencia}")
    else:
        md.append('- No se detectaron evidencias con la convencion esperada.')
    md.append('')

    if files_info['large_files']:
        md.append('## Archivos grandes (>=10MB)')
        for lf in files_info['large_files']:
            md.append(f"- {lf['path']} - {lf['size']} bytes")
        md.append('')

    md.append('## Arbol del repositorio (resumen)')
    md.append('```')
    md.append(safe_read_text(outdir / 'arbol.txt')[:4000])
    md.append('```')

    (outdir / 'informe.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f"Informe generado en: {outdir}/informe.md")


if __name__ == '__main__':
    main()
