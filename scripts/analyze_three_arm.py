"""Derive a readable diagnostic report without altering collected evidence."""
import difflib
import json
import pathlib
import sys


def analyse(directory):
    root = pathlib.Path(directory)
    analysis = json.loads((root / 'analysis.json').read_text())
    runs = json.loads((root / 'runs.json').read_text())
    lines = ['# Three-arm diagnostic: actual results', '',
             f"Generation calls: {analysis['completed']} parsed; {analysis['failed']} failed.",
             'Model: deepseek-v4-flash. Temperature 0.75; max_tokens 3500.', '',
             '| Arm | Pass | n | Cites prior position | Predicted conclusion change | Unclear |',
             '|---|---:|---:|---:|---:|---:|']
    for arm, passes in analysis['rates'].items():
        for i, score in enumerate(passes):
            n = score['n']
            lines.append(f"| {arm} | {i+1} | {n} | {score['cites']}/{n} | {score['change']}/{n} | {score['unclear']}/{n} |")
    lines += ['', f"Transcripts with at least one evaluator disagreement: {len(analysis['disagreements'])}.", '',
              '## Removal versus sampling variation', '']
    by_arm = {r['arm']: r for r in runs if r['slot'] == 1 and r.get('parsed')}
    for arm in ['removal', 'sham']:
        if arm not in by_arm or 'C' not in by_arm:
            lines.append(f'{arm}: unavailable because a call failed.')
            continue
        base, other = by_arm['C']['parsed'], by_arm[arm]['parsed']
        sim = difflib.SequenceMatcher(None, base['reply'], other['reply'], autojunk=False).ratio()
        same = base.get('belief_updates') == other.get('belief_updates')
        lines.append(f'- C versus {arm}: text similarity {sim:.3f}; belief updates identical: {same}.')
    lines += ['', 'Text similarity is a lexical diagnostic, not a causal effect measure. '
              'Different unchanged-state responses establish that wording changes alone cannot '
              'be attributed to belief deletion. A single pair cannot estimate the noise distribution.', '',
              '## Interpretation boundaries', '',
              'A contextual input can have a causal effect. These are not opposing mechanisms. '
              'External-state influence does not imply changed model weights or inference machinery.', '',
              'The two score questions concern the evaluator\'s interpretation of written reasoning. '
              'They do not directly measure independence, creativity, or long-horizon utility. '
              'The historical state was reconstructed, and each slot branches from it independently.', '']
    lines += ['- ' + item for item in analysis['limitations']]
    lines += ['', '## Next engineering decision', '',
              'Keep active-policy promotion closed. Use independently generated tasks with known '
              'premise dependencies, verify complete removal of redundant premise copies, and '
              'compare held-out decisions under repeated removal and sham trials. Calibrate the '
              'scorer against those observed interventions before using it to select agent policies.', '',
              'Raw records, sealed prompts, blinded packets, evaluator responses and disagreement '
              'IDs are stored beside this report. No old records were overwritten.']
    target = root / 'RESULTS.md'
    with target.open('x') as stream:
        stream.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    analyse(sys.argv[1])
