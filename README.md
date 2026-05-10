# 📚 Q&A 커뮤니티 데이터베이스 설계 및 구현
> **서울대학교 데이터관리와 분석(406.426B) Project 1**

온라인 Q&A 커뮤니티의 요구사항을 분석하여 9개의 엔티티와 16개의 관계를 가진 관계형 데이터베이스를 설계하고, MySQL을 통해 대용량 데이터를 처리할 수 있도록 구현한 프로젝트입니다.

## 📊 ER Diagram
> 깃허브 Mermaid 라이브러리를 활용한 DB 구조 시각화입니다.

```mermaid
erDiagram
    USERS ||--o{ POSTS : writes
    USERS ||--o{ COMMENTS : "writes comment"
    USERS ||--o{ VOTES : "votes by"
    USERS ||--o{ BADGES : "has badges"
    USERS ||--o{ POSTHISTORY : "performed by"
    
    POSTS ||--|| QUESTION : is_question
    POSTS ||--|| ANSWER : is_answer
    POSTS ||--o{ COMMENTS : "has comment"
    POSTS ||--o{ VOTES : "has_votes"
    POSTS ||--o{ POSTHISTORY : "has history"
    POSTS ||--o{ POSTLINKS : "post links"
    
    QUESTION ||--o| ANSWER : "accepted answer"
    QUESTION ||--o{ ANSWER : has
    
    POSTS ||--o| TAGS : "has excerpt/wiki"
