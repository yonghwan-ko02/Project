#!/usr/bin/env python3
"""
GitHub Issues 동기화 스크립트
Task.md의 작업 항목들을 GitHub Issues와 동기화합니다.
"""

import json
import re
import subprocess
import sys
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


def parse_task_md(file_path: str) -> List[Dict[str, any]]:
    """Task.md 파일을 파싱하여 작업 항목 추출"""
    tasks = []
    current_phase = None
    current_main_task = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.rstrip()
        
        # Phase 헤더 감지
        if line.startswith('## Phase'):
            current_phase = line.replace('## ', '').strip()
            continue
        
        # 메인 작업 항목 (- [ ] **작업명**)
        main_task_match = re.match(r'^- \[([ x/])\] \*\*(.+?)\*\*', line)
        if main_task_match:
            status = main_task_match.group(1)
            title = main_task_match.group(2)
            current_main_task = {
                'phase': current_phase,
                'title': title,
                'status': status,
                'subtasks': [],
                'level': 'main'
            }
            tasks.append(current_main_task)
            continue
        
        # 서브 작업 항목 (    - [ ] 작업명)
        sub_task_match = re.match(r'^    - \[([ x/])\] (.+)', line)
        if sub_task_match and current_main_task:
            status = sub_task_match.group(1)
            title = sub_task_match.group(2)
            subtask = {
                'phase': current_phase,
                'title': title,
                'status': status,
                'parent': current_main_task['title'],
                'level': 'sub'
            }
            current_main_task['subtasks'].append(subtask)
            continue
        
        # 세부 작업 항목 (        - [ ] 작업명)
        detail_task_match = re.match(r'^        - \[([ x/])\] (.+)', line)
        if detail_task_match and current_main_task and current_main_task['subtasks']:
            status = detail_task_match.group(1)
            title = detail_task_match.group(2)
            detail = {
                'phase': current_phase,
                'title': title,
                'status': status,
                'parent': current_main_task['subtasks'][-1]['title'],
                'level': 'detail'
            }
            current_main_task['subtasks'][-1].setdefault('details', []).append(detail)
    
    return tasks


def get_existing_issues(repo: str) -> List[Dict[str, any]]:
    """GitHub CLI를 사용하여 기존 이슈 조회"""
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--repo', repo, '--limit', '100', 
             '--json', 'number,title,state,labels,body'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching issues: {e}")
        sys.exit(1)


def similarity_score(a: str, b: str) -> float:
    """두 문자열의 유사도 계산 (0.0 ~ 1.0)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_matching_issue(task: Dict, existing_issues: List[Dict]) -> Dict | None:
    """작업 항목과 매칭되는 기존 이슈 찾기"""
    best_match = None
    best_score = 0.0
    threshold = 0.6  # 유사도 임계값
    
    task_title = task['title']
    
    for issue in existing_issues:
        score = similarity_score(task_title, issue['title'])
        if score > best_score and score >= threshold:
            best_score = score
            best_match = issue
    
    return best_match


def generate_issue_body(task: Dict) -> str:
    """이슈 본문 생성 (작업 배경, 작업 내용, 인수 조건 포함)"""
    phase = task.get('phase', 'N/A')
    title = task['title']
    
    # 작업 배경
    background = f"**Phase**: {phase}\n\n"
    background += "이 작업은 전래동화 리부트 프로젝트의 일환으로, "
    
    if 'Phase 1' in phase:
        background += "프로젝트 환경 설정 및 기초 공사를 위한 작업입니다."
    elif 'Phase 2' in phase:
        background += "LoreKeeper 데이터 엔지니어링을 위한 작업입니다. SOLID 원칙과 TDD를 적용합니다."
    elif 'Phase 3' in phase:
        background += "DungeonMaster AI 엔진 구현을 위한 작업입니다. SOLID 원칙과 TDD를 적용합니다."
    elif 'Phase 4' in phase:
        background += "GameLoop 게임 시스템 구축을 위한 작업입니다. UI와 로직을 분리합니다."
    elif 'Phase 5' in phase:
        background += "인터페이스 및 통합 작업입니다. 실제 컴포넌트 연동 및 테스트를 수행합니다."
    elif 'Phase 6' in phase:
        background += "폴리싱 및 확장 작업입니다. 안정성과 사용자 경험을 개선합니다."
    
    # 작업 내용
    work_content = f"\n\n**작업 내용**:\n{title}\n"
    
    # 서브태스크가 있으면 추가
    if task.get('subtasks'):
        work_content += "\n**세부 작업**:\n"
        for subtask in task['subtasks']:
            work_content += f"- {subtask['title']}\n"
            if subtask.get('details'):
                for detail in subtask['details']:
                    work_content += f"  - {detail['title']}\n"
    
    # 인수 조건
    acceptance_criteria = "\n\n**인수 조건 (Acceptance Criteria)**:\n"
    
    if task.get('subtasks'):
        for subtask in task['subtasks']:
            acceptance_criteria += f"- [ ] {subtask['title']}\n"
    else:
        # 서브태스크가 없으면 기본 인수 조건 생성
        if 'TDD' in title or 'Test' in title:
            acceptance_criteria += "- [ ] 테스트 코드 작성 완료\n"
            acceptance_criteria += "- [ ] 모든 테스트 통과\n"
        if '구현' in title or 'Implement' in title:
            acceptance_criteria += "- [ ] 기능 구현 완료\n"
            acceptance_criteria += "- [ ] 코드 리뷰 완료\n"
        if '설계' in title or 'Design' in title:
            acceptance_criteria += "- [ ] 인터페이스 정의 완료\n"
            acceptance_criteria += "- [ ] 설계 문서 작성 완료\n"
        
        # 기본 인수 조건
        acceptance_criteria += "- [ ] 관련 문서 업데이트\n"
    
    return f"**작업 배경 (Background)**:\n{background}{work_content}{acceptance_criteria}"


def create_issue(repo: str, title: str, body: str, dry_run: bool = False) -> bool:
    """GitHub 이슈 생성"""
    if dry_run:
        print(f"\n[DRY RUN] 이슈 생성 예정:")
        print(f"제목: {title}")
        print(f"본문:\n{body}")
        print("-" * 80)
        return True
    
    try:
        result = subprocess.run(
            ['gh', 'issue', 'create', '--repo', repo, '--title', title, '--body', body],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ 이슈 생성 완료: {title}")
        print(f"  URL: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 이슈 생성 실패 '{title}': {e}")
        return False


def main():
    # 설정
    REPO = "yonghwan-ko02/Project"
    TASK_MD_PATH = "docs/Task.md"
    DRY_RUN = '--dry-run' in sys.argv
    
    if DRY_RUN:
        print("=" * 80)
        print("DRY RUN 모드 - 이슈가 생성되지 않습니다")
        print("=" * 80)
    
    # Task.md 파싱
    print(f"\n📖 {TASK_MD_PATH} 파싱 중...")
    tasks = parse_task_md(TASK_MD_PATH)
    print(f"   {len(tasks)}개의 메인 작업 발견")
    
    # 기존 이슈 조회
    print(f"\n🔍 {REPO}에서 기존 이슈 조회 중...")
    existing_issues = get_existing_issues(REPO)
    print(f"   {len(existing_issues)}개의 기존 이슈 발견")
    
    # 비교 및 동기화
    print(f"\n🔄 작업 항목과 기존 이슈 비교 중...")
    
    new_issues_count = 0
    matched_count = 0
    
    for task in tasks:
        # 메인 작업만 이슈로 생성 (서브태스크는 본문에 포함)
        if task['level'] != 'main':
            continue
        
        matching_issue = find_matching_issue(task, existing_issues)
        
        if matching_issue:
            matched_count += 1
            print(f"   ✓ 매칭됨: '{task['title']}' → 이슈 #{matching_issue['number']}")
        else:
            # 새로운 이슈 생성 필요
            title = task['title']
            body = generate_issue_body(task)
            
            if create_issue(REPO, title, body, dry_run=DRY_RUN):
                new_issues_count += 1
    
    # 결과 요약
    print(f"\n" + "=" * 80)
    print(f"📊 요약:")
    print(f"   Task.md 전체 작업 수: {len(tasks)}")
    print(f"   기존 이슈 수: {len(existing_issues)}")
    print(f"   매칭된 작업 수: {matched_count}")
    print(f"   {'생성 예정' if DRY_RUN else '생성된'} 신규 이슈 수: {new_issues_count}")
    print("=" * 80)
    
    if DRY_RUN:
        print("\n💡 실제로 이슈를 생성하려면 --dry-run 옵션 없이 실행하세요")


if __name__ == "__main__":
    main()
