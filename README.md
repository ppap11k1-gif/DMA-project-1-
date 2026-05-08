# Stack Overflow Style Q&A Community Database Engineering
> **개념적 모델링부터 대규모 데이터 ETL 파이프라인 구축까지의 End-to-End 프로세스**

[cite_start]본 프로젝트는 대규모 사용자가 상호작용하는 온라인 Q&A 커뮤니티의 복잡한 비즈니스 로직을 분석하여, **정규화된 관계형 데이터베이스(RDB)**를 설계하고 약 100만 건 이상의 실제 레코드를 안정적으로 적재하는 시스템을 구축한 프로젝트입니다[cite: 387, 388, 975, 976].

## 1. 프로젝트 개요 및 핵심 요구사항 (Problem Definition)
[cite_start]단순한 데이터 저장을 넘어, 커뮤니티 내의 다양한 상호작용(질문-답변-댓글-투표) 간의 **무결성(Integrity)**을 유지하고, 데이터 분석에 최적화된 스키마를 도출하는 것을 목표로 합니다[cite: 394, 982].

### 1.1 주요 요구사항 (Requirements Analysis)
* [cite_start]**사용자 및 활동 관리**: 평판(Reputation), 가입일, 뱃지 획득 이력 관리[cite: 401, 403, 989, 991].
* [cite_start]**콘텐츠 계층 구조**: 게시물(Posts) 내 질문(Question)과 답변(Answer)의 상호 배타적 관계 정의[cite: 40, 51, 406, 631, 642, 994].
* [cite_start]**상호작용 추적**: 게시물별 댓글(Comments), 투표(Votes), 수정 이력(PostHistory) 기록[cite: 403, 991].
* [cite_start]**데이터 연결성**: 태그(Tags) 시스템 및 게시물 간 인용/참조(PostLinks) 관계 구축[cite: 403, 416, 633, 991, 1004].

## 2. 개념적 데이터 모델링 (Conceptual Design)
[cite_start]총 10가지의 비즈니스 요구사항을 분석하여 **9개의 핵심 엔티티(Entity)**와 **16개의 관계(Relationship)**를 도출했습니다[cite: 63, 143, 144, 356, 430, 586, 654, 734, 735, 1174].

### 2.1 주요 설계 결정 (Technical Decisions)
* **상호 배타적 제약(Disjoint Constraints) 처리**: 
    * [cite_start]하나의 `Post`는 반드시 `Question` 또는 `Answer` 중 하나에만 속해야 합니다[cite: 40, 51, 62, 360, 406, 587, 631, 642, 653, 994, 1175].
    * [cite_start]EER Specialization 대신 **1:1 관계**를 설정하고 논리적 제약 조건을 명시하여 물리적 데이터셋 구조와의 정합성을 확보했습니다[cite: 40, 408, 631, 996].
* **M:N Recursive Relationship 설계**:
    * [cite_start]게시물 간의 연결(`PostLinks`)을 독립 엔티티가 아닌 `Posts` 간의 **M:N 재귀 관계**로 모델링하여 스키마의 복잡도를 낮추고 유연성을 확보했습니다[cite: 43, 419, 634, 1007].
* **약한 엔티티(Weak Entity) 식별**:
    * [cite_start]댓글(`Comments`)은 게시물에 종속된 구조이므로 `(Id, PostId)` 복합키를 활용한 약한 엔티티로 정의하여 데이터 종속성을 명확히 했습니다[cite: 173, 403, 764, 991].

## 3. 물리적 스키마 설계 (Physical Design)
[cite_start]MySQL(InnoDB) 엔진을 기반으로 대규모 읽기/쓰기 성능을 고려한 데이터 타입을 매핑하고 제약 조건을 설정했습니다[cite: 150, 447, 741, 1035].

### 3.1 주요 테이블 구조
| 테이블명 | 주요 특징 | 물리적 제약 조건 |
| :--- | :--- | :--- |
| **Users** | [cite_start]사용자 기본 정보 및 활동 지표 관리 [cite: 468, 1056] | [cite_start]**PK:** UserId [cite: 470, 1058] |
| **Posts** | [cite_start]질문/답변의 공통 속성 저장 [cite: 471, 1059] | [cite_start]**PK:** Id, **FK:** OwnerUserId [cite: 472, 577, 1060, 1165] |
| **Question** | [cite_start]질문 고유 속성 (ViewCount, Title 등) [cite: 473, 1061] | [cite_start]**PK:** Id, **UNIQUE:** PostId [cite: 474, 519, 1062, 1107] |
| **Answer** | [cite_start]답변 여부 및 질문과의 연결 [cite: 475, 1063] | [cite_start]**PK:** Id, **UNIQUE:** PostId [cite: 476, 496, 1064, 1084] |
| **Comments** | [cite_start]게시물 종속 댓글 관리 [cite: 477, 1065] | [cite_start]**Composite PK:** (Id, PostId) [cite: 478, 527, 1066, 1115] |

## 4. 데이터 적재 파이프라인 (ETL Process)
[cite_start]Python 3.14.3과 `mysql-connector-python`을 활용하여 10개의 원천 데이터(CSV)를 정제 및 적재하는 스크립트를 구현했습니다[cite: 150, 452, 741, 1040].

### 4.1 성능 최적화 전략
* [cite_start]**Batch Insertion**: 단건 삽입의 오버헤드를 방지하기 위해 **1,000건 단위의 배치 적재 전략**을 적용했습니다[cite: 319, 534, 571, 1122, 1159].
* [cite_start]**Memory Management**: `innodb_buffer_pool_size` 설정을 통해 대용량 데이터 삽입 시 인덱스 갱신 성능을 확보했습니다[cite: 262, 460, 853, 1048].
* [cite_start]**전처리 파이프라인**: 비표준 날짜(`YYYY.M.D`)를 MySQL 표준 `DATETIME`으로 자동 변환하고 결측치를 `NULL`로 매핑하는 로직을 구축했습니다[cite: 524, 555, 1112, 1143].

## 5. 트러블슈팅: 데이터 무결성 및 장애 대응

### 5.1 데이터 이상치(Anomaly) 해결
* [cite_start]**문제**: `comments.csv` 적재 중 동일 게시물 내 중복 순번을 가진 **1,727건의 중복 레코드** 발견[cite: 177, 362, 526, 531, 768, 1114].
* [cite_start]**해결**: 원본 수정을 금지하는 제약 하에, **물리적 복합키 제약**을 활용하여 중복 행만 안전하게 스킵함으로써 데이터 정합성을 확보했습니다[cite: 175, 527, 766, 1115].

### 5.2 안정적 삽입 로직 (Fault Tolerance)
* [cite_start]배치 삽입 실패 시 전체를 **Rollback**한 뒤, 해당 묶음만 **한 줄씩 재시도(Row-by-row Retry)**하여 불량 데이터만 선별적으로 격리하는 방어적 로직을 탑재했습니다 [cite: 281-292, 534-547, 872-883, 1122-1135].

## 6. 프로젝트 결과물
* **핵심 스크립트**: [DMA_project1_team15.py](./DMA_project1_team15.py)
* **상세 보고서**: [기술 설계 명세서](./DMA_project1_보고서_이름삭제.pdf)
* **발표 자료**: [스키마 요약 및 결과 지표](./DMA_project1_발표자료_이름삭제.pdf)

---
**Note:** 본 프로젝트는 교육용 데이터셋을 기반으로 하며, 저작권 및 보안 준수를 위해 원천 CSV 데이터는 포함하고 있지 않습니다.
