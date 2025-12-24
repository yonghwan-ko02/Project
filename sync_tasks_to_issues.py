#!/usr/bin/env python3
"""
Sync tasks from docs/Task.md to GitHub Issues.
Creates new issues for tasks that don't already exist.
"""

import json
import re
import subprocess
import sys
from typing import List, Dict, Tuple


def run_gh_command(args: List[str]) -> str:
    """Run a gh CLI command and return the output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_existing_issues() -> List[Dict]:
    """Fetch all existing GitHub issues."""
    output = run_gh_command(["issue", "list", "--limit", "1000", "--json", "number,title,labels,state"])
    return json.loads(output) if output else []


def parse_task_md(file_path: str) -> List[Dict]:
    """Parse docs/Task.md and extract tasks organized by phase."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = []
    current_phase = None
    current_phase_num = None
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Match phase headers: ## Phase N: Title
        phase_match = re.match(r'^## (Phase \d+):\s*(.+?)(?:\s*\([^)]+\))?\s*$', line)
        if phase_match:
            current_phase_num = phase_match.group(1)
            current_phase = phase_match.group(2).strip()
            i += 1
            continue
        
        # Match top-level tasks: - [ ] **Task Name**
        task_match = re.match(r'^- \[ \] \*\*(.+?)\*\*\s*$', line)
        if task_match and current_phase:
            task_name = task_match.group(1)
            
            # Collect sub-tasks (indented items)
            sub_tasks = []
            i += 1
            while i < len(lines):
                sub_line = lines[i]
                # Match indented sub-tasks
                if re.match(r'^\s+- \[ \]', sub_line):
                    sub_tasks.append(sub_line.strip())
                    i += 1
                elif sub_line.strip() == '':
                    i += 1
                    continue
                else:
                    break
            
            tasks.append({
                'phase': current_phase,
                'phase_num': current_phase_num,
                'name': task_name,
                'sub_tasks': sub_tasks
            })
            continue
        
        i += 1
    
    return tasks


def create_issue_body(task: Dict) -> str:
    """Create formatted issue body with background, content, and acceptance criteria."""
    body = f"## 작업 배경 (Background)\n\n"
    body += f"**{task['phase_num']}**의 일환으로, {task['name']} 작업을 수행합니다.\n\n"
    
    body += f"## 작업 내용 (Work Content)\n\n"
    if task['sub_tasks']:
        for sub_task in task['sub_tasks']:
            body += f"{sub_task}\n"
    else:
        body += f"{task['name']} 구현\n"
    
    body += f"\n## 완료 조건 (Acceptance Criteria)\n\n"
    body += f"- [ ] 모든 하위 작업이 완료됨\n"
    
    # Add TDD requirement for core logic phases
    if any(keyword in task['phase'].lower() for keyword in ['lorekeeper', 'dungeonmaster', 'gameloop', 'data engineering', 'ai engine', 'game system']):
        body += f"- [ ] TDD 원칙에 따라 테스트 코드 작성 완료\n"
        body += f"- [ ] SOLID 원칙 준수 확인\n"
    
    body += f"- [ ] 관련 문서 업데이트 완료\n"
    
    return body


def create_github_issue(task: Dict) -> bool:
    """Create a GitHub issue for the given task."""
    title = f"{task['name']}"
    body = create_issue_body(task)
    
    try:
        print(f"Creating issue: {title}")
        # Create issue without labels since they may not exist
        run_gh_command([
            "issue", "create",
            "--title", title,
            "--body", body
        ])
        print(f"[OK] Created: {title}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create issue '{title}': {e}", file=sys.stderr)
        return False


def normalize_title(title: str) -> str:
    """Normalize title for comparison (remove extra spaces, parentheses content, etc.)."""
    # Remove content in parentheses
    title = re.sub(r'\s*\([^)]+\)\s*', '', title)
    # Remove extra whitespace
    title = ' '.join(title.split())
    return title.lower().strip()


def main():
    print("=" * 60)
    print("Syncing tasks from docs/Task.md to GitHub Issues")
    print("=" * 60)
    
    # Parse Task.md
    print("\n[1/4] Parsing docs/Task.md...")
    tasks = parse_task_md('docs/Task.md')
    print(f"Found {len(tasks)} tasks in Task.md")
    
    # Get existing issues
    print("\n[2/4] Fetching existing GitHub issues...")
    existing_issues = get_existing_issues()
    print(f"Found {len(existing_issues)} existing issues")
    
    # Normalize existing issue titles for comparison
    existing_titles = {normalize_title(issue['title']) for issue in existing_issues}
    
    # Find new tasks
    print("\n[3/4] Comparing tasks with existing issues...")
    new_tasks = []
    for task in tasks:
        normalized_task_name = normalize_title(task['name'])
        if normalized_task_name not in existing_titles:
            new_tasks.append(task)
            print(f"  -> New task found: {task['name']}")
        else:
            print(f"  [OK] Already exists: {task['name']}")
    
    # Create new issues
    print(f"\n[4/4] Creating {len(new_tasks)} new issues...")
    if not new_tasks:
        print("No new tasks to sync. All tasks already have corresponding issues!")
        return
    
    created_count = 0
    for task in new_tasks:
        if create_github_issue(task):
            created_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary: Created {created_count}/{len(new_tasks)} new issues")
    print("=" * 60)


if __name__ == "__main__":
    main()
