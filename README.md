# Stack Overflow Style Q&A Database Engineering
> **개념적 설계부터 물리적 구현까지: 대규모 커뮤니티 데이터셋을 위한 고가용성 RDB 구축**

[cite_start]본 프로젝트는 온라인 Q&A 커뮤니티의 복잡한 비즈니스 로직을 분석하여 **정규화된 관계형 데이터베이스(RDB)**를 설계하고, 약 100만 건 이상의 대규모 레코드를 안정적으로 적재하기 위한 **데이터 파이프라인**을 구축한 프로젝트입니다. [cite: 387, 388, 586]

## 1. 프로젝트 아키텍처 및 기술 스택
* [cite_start]**Language:** Python 3.14.3 [cite: 150, 452]
* [cite_start]**Database:** MySQL (InnoDB Engine) [cite: 150, 447]
* [cite_start]**Interface:** `mysql-connector-python` [cite: 452]
* [cite_start]**Architecture:** 9 Entities, 16 Relationships [cite: 356, 1174]

## 2. 데이터 모델링 핵심 전략 (Conceptual Design)

### 2.1 상호 배타적(Disjoint) 제약 조건의 물리적 구현
* [cite_start]**Challenge:** 게시물(`Posts`) 엔티티는 반드시 '질문' 또는 '답변' 중 하나에만 속해야 함. [cite: 40, 51, 631]
* [cite_start]**Solution:** EER Specialization 기호 대신 **1:1 관계(IS_QUESTION, IS_ANSWER)**를 설정하고, `PostId`에 `UNIQUE` 제약을 부여하여 물리적 정합성을 강제했습니다. [cite: 408, 411, 412, 519, 520]

### 2.2 관계 차수(Cardinality) 및 참여 제약 조건 최적화
* [cite_start]**M:N Recursive Relationship:** 게시물 간 연결 관계(`PostLinks`)를 독립 엔티티가 아닌 **M:N 재귀 관계**로 모델링하여 복잡도를 줄였습니다. [cite: 43, 419, 420]
* [cite_start]**Weak Entity 식별:** 댓글(`Comments`)은 게시물에 종속된 구조이므로 `(Id, PostId)` 복합키를 활용한 약한 엔티티로 정의했습니다. [cite: 173, 527, 764]

## 3. 고성능 데이터 마이그레이션 (Implementation)

### 3.1 Batch Insert & 로직 최적화
* [cite_start]**성능 최적화:** 단건 삽입의 오버헤드를 줄이기 위해 `executemany()` 메서드를 활용, **1,000건 단위의 배치 삽입 전략**을 구현했습니다. [cite: 284, 533, 1121]
* [cite_start]**전처리 파이프라인:** 비표준 날짜 데이터(`YYYY.M.D HH:MM`)를 MySQL 표준 `DATETIME` 형식으로 변환하고, 결측치를 자동 감지하여 `NULL`로 매핑하는 로직을 구축했습니다. [cite: 524, 1112]

### 3.2 Robust 에러 핸들링 (Data Reliability)
* [cite_start]**Transaction 관리:** 삽입 시 예외 발생 시 즉시 `rollback()`을 수행합니다. [cite: 286, 541, 1129]
* [cite_start]**Fall-back 전략:** 배치 삽입 실패 시, 해당 묶음을 **한 줄씩 재시도(Row-by-row Retry)**하여 불량 데이터만 선별적으로 스킵하고 데이터 유실을 최소화하는 방어적 로직을 구현했습니다. [cite: 287-292, 542-547, 1130-1135]

## 4. 트러블슈팅: 데이터 이상치(Anomaly) 처리
* [cite_start]**발견:** `comments.csv` 적재 중 동일 게시물 내 중복 순번을 가진 **1,727건의 중복 데이터** 감지. [cite: 177, 526, 768]
* [cite_start]**해결:** 데이터 무결성 원칙에 따라 원본 소스를 수정하지 않고, **DB 수준의 복합 Primary Key** 제약을 통해 중복 삽입을 원천 차단하여 데이터 정합성을 100% 확보했습니다. [cite: 175, 527, 766]

## 5. 프로젝트 구조 및 파일 설명
* `DMA_project1_team15.py`: DB 스키마 생성 및 데이터 적재 전체 자동화 스크립트
* `DMA_project1_보고서.pdf`: ERD 도출 논리, 카디널리티 분석 및 제약 조건 명세
* `DMA_project1_발표자료.pdf`: 프로젝트 핵심 성과 요약 및 스키마 시각화 자료

---
[cite_start]**Note:** 본 프로젝트는 데이터 보안 및 저작권 준수를 위해 원천 CSV 데이터는 포함하고 있지 않으나, 제공된 파이썬 스크립트를 통해 설계된 데이터 파이프라인 구조를 모두 확인할 수 있습니다. [cite: 175, 525, 1113]
