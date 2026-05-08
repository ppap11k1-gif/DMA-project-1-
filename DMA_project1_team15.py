import mysql.connector
import csv


# TODO: REPLACE THE VALUE OF VARIABLE team (EX. TEAM 1 --> team = 1)
team = 15


# Requirement1: create schema ( name: DMA_team15 )
def requirement1(host, user, password):
    cnx = mysql.connector.connect(host=host, user=user, password=password)
    cursor = cnx.cursor()
    cursor.execute('SET GLOBAL innodb_buffer_pool_size=2*1024*1024*1024;')
    print('Creating schema...')


    # TODO: WRITE CODE HERE
    cursor.execute('CREATE SCHEMA IF NOT EXISTS DMA_team15;')
    cnx.commit()

    cursor.close()
    cnx.close()


# Requierement2: create table
def requirement2(host, user, password):
    cnx = mysql.connector.connect(host=host, user=user, password=password)
    cursor = cnx.cursor()
    cursor.execute('SET GLOBAL innodb_buffer_pool_size=2*1024*1024*1024;')
    print('Creating tables...')

    # TODO: WRITE CODE HERE
    cursor.execute('USE DMA_team15;')

    # users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            UserId INT(11) NOT NULL,
            Reputation INT(11) NOT NULL,
            DisplayName VARCHAR(255) NOT NULL,
            Age INT(11),
            CreationDate DATETIME NOT NULL,
            LastAccessDate DATETIME NOT NULL,
            WebsiteUrl VARCHAR(255),
            Location VARCHAR(255),
            AboutMe LONGTEXT,
            PRIMARY KEY (UserId)
        )
    ''')

    # posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            Id INT(11) NOT NULL,
            CreationDate DATETIME NOT NULL,
            Content LONGTEXT NOT NULL,
            OwnerUserId INT(11),
            LasActivityDate DATETIME NOT NULL,
            PRIMARY KEY (Id)
        )
    ''')

    # question
    # NOTE: IS_QUESTION(1:1) 관계 → PostId UNIQUE.
    #       accepted(1:1) 관계 → AcceptedAnswerId UNIQUE (nullable이므로 NULL 중복은 허용).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question (
            Id INT(11) NOT NULL,
            PostId INT(11) NOT NULL,
            AcceptedAnswerId INT(11),
            ViewCount INT(11) NOT NULL,
            Title VARCHAR(255) NOT NULL,
            Tags VARCHAR(255) NOT NULL,
            PRIMARY KEY (Id),
            UNIQUE (PostId),
            UNIQUE (AcceptedAnswerId)
        )
    ''')

    # answer
    # NOTE: Accepted 컬럼은 실제 데이터가 {1, 2} 값을 가지므로 R2-2 규칙에 따라
    #       0/1 전용 TINYINT(1)가 아닌 일반 정수 INT(11)로 생성한다.
    # NOTE: IS_ANSWER(1:1) 관계 → PostId UNIQUE.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answer (
            Id INT(11) NOT NULL,
            PostId INT(11) NOT NULL,
            Accepted INT(11) NOT NULL,
            ParentId INT(11) NOT NULL,
            PRIMARY KEY (Id),
            UNIQUE (PostId)
        )
    ''')

    # comments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            Id INT(11) NOT NULL,
            PostId INT(11) NOT NULL,
            Score INT(11) NOT NULL,
            CreationDate DATETIME NOT NULL,
            UserInfoId INT(11) NOT NULL,
            PRIMARY KEY (Id, PostId)
        )
    ''')

    # votes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            Id INT(11) NOT NULL,
            PostId INT(11) NOT NULL,
            VoteTypeId INT(11) NOT NULL,
            CreationDate DATETIME NOT NULL,
            UserInfoId INT(11),
            BountyAmount INT(11),
            PRIMARY KEY (Id)
        )
    ''')

    # tags
    # NOTE: ExcerptPostId/WikiPostId는 각 Tag가 최대 하나의 Post와 대응되는
    #       구현 수준 1:1 관계이므로 UNIQUE 제약을 추가한다 (nullable).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            Id INT(11) NOT NULL,
            TagName VARCHAR(255) NOT NULL,
            ExcerptPostId INT(11),
            WikiPostId INT(11),
            PRIMARY KEY (Id),
            UNIQUE (ExcerptPostId),
            UNIQUE (WikiPostId)
        )
    ''')

    # badges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            Id INT(11) NOT NULL,
            UserInfoId INT(11) NOT NULL,
            Name VARCHAR(255) NOT NULL,
            Date DATETIME NOT NULL,
            PRIMARY KEY (Id)
        )
    ''')

    # postHistory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postHistory (
            Id INT(11) NOT NULL,
            PostHistoryTypeId INT(11) NOT NULL,
            PostId INT(11) NOT NULL,
            CreationDate DATETIME NOT NULL,
            UserInfoId INT(11),
            Text LONGTEXT,
            Comment LONGTEXT,
            PRIMARY KEY (Id)
        )
    ''')

    # postLinks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postLinks (
            Id INT(11) NOT NULL,
            CreationDate DATETIME NOT NULL,
            PostId INT(11) NOT NULL,
            RelatedPostId INT(11) NOT NULL,
            LinkTypeId INT(11) NOT NULL,
            PRIMARY KEY (Id)
        )
    ''')

    cnx.commit()
    cursor.close()
    cnx.close()


# Requirement3: insert data
def requirement3(host, user, password, directory):
    cnx = mysql.connector.connect(host=host, user=user, password=password)
    cursor = cnx.cursor()
    cursor.execute('SET GLOBAL innodb_buffer_pool_size=2*1024*1024*1024;')
    print('Inserting data...')


    # TODO: WRITE CODE HERE
    cursor.execute('USE DMA_team15;')

    BATCH_SIZE = 1000

    def convert_dot_date(val):
        """'2010.7.19 19:12' -> '2010-07-19 19:12:00'"""
        if not val or val == '':
            return None
        parts = val.split(' ')
        date_parts = parts[0].split('.')
        time_part = parts[1] if len(parts) > 1 else '00:00'
        return f"{int(date_parts[0]):04d}-{int(date_parts[1]):02d}-{int(date_parts[2]):02d} {time_part}:00"

    def to_int(val):
        return int(val) if val and val != '' else None

    def to_str(val):
        return val if val and val != '' else None

    def flush(cursor, cnx, sql, batch):
        if batch:
            try:
                # 1. 먼저 1000개 단위로 빠르게 삽입 시도
                cursor.executemany(sql, batch)
            except mysql.connector.Error:
                # 2. 에러가 발생하면, 방금 1000개를 넣으려다 일부만 들어간 상태를 즉시 롤백
                cnx.rollback()

                # 3. 한 줄씩 다시 넣기
                for row in batch:
                    try:
                        cursor.execute(sql, row)
                    except mysql.connector.Error:
                        # 4. 또 에러가 난다면,불량 데이터 1줄이므로 가볍게 무시하고 다음 줄로 
                        pass
            cnx.commit()

    def read_csv(filepath):
        return csv.reader(open(filepath, 'r', encoding='utf-8', errors='replace'))

    # --- users (40,325 rows) ---
    print('  Inserting users...')
    reader = read_csv(directory + 'users.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),                # UserId
            int(row[1]),                # Reputation
            row[2],                     # DisplayName
            to_int(row[3]),             # Age
            convert_dot_date(row[4]),   # CreationDate
            convert_dot_date(row[5]),   # LastAccessDate
            to_str(row[6]),             # WebsiteUrl
            to_str(row[7]),             # Location
            to_str(row[8]) if len(row) > 8 else None,  # AboutMe
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', batch)

    # --- posts (91,977 rows, multiline Content) ---
    print('  Inserting posts...')
    reader = read_csv(directory + 'posts.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),                # Id
            convert_dot_date(row[1]),   # CreationDate
            row[2],                     # Content
            to_int(row[3]),             # OwnerUserId
            convert_dot_date(row[4]),   # LasActivityDate
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO posts VALUES (%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO posts VALUES (%s,%s,%s,%s,%s)', batch)

    # --- question (42,921 rows) ---
    print('  Inserting question...')
    reader = read_csv(directory + 'question.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),        # Id
            int(row[1]),        # PostId
            to_int(row[2]),     # AcceptedAnswerId
            int(row[3]),        # ViewCount
            row[4],             # Title
            row[5],             # Tags
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO question VALUES (%s,%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO question VALUES (%s,%s,%s,%s,%s,%s)', batch)

    # --- answer (47,756 rows) ---
    print('  Inserting answer...')
    reader = read_csv(directory + 'answer.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),    # Id
            int(row[1]),    # PostId
            int(row[2]),    # Accepted
            int(row[3]),    # ParentId
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO answer VALUES (%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO answer VALUES (%s,%s,%s,%s)', batch)

    # --- comments (171,470 rows) ---
    print('  Inserting comments...')
    reader = read_csv(directory + 'comments.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),    # Id
            int(row[1]),    # PostId
            int(row[2]),    # Score
            row[3],         # CreationDate (ISO format)
            int(row[4]),    # UserInfoId
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO comments VALUES (%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO comments VALUES (%s,%s,%s,%s,%s)', batch)

    # --- votes (323,233 rows) ---
    print('  Inserting votes...')
    reader = read_csv(directory + 'votes.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),        # Id
            int(row[1]),        # PostId
            int(row[2]),        # VoteTypeId
            row[3],             # CreationDate (date-only, OK for DATETIME)
            to_int(row[4]),     # UserInfoId
            to_int(row[5]) if len(row) > 5 else None,  # BountyAmount
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO votes VALUES (%s,%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO votes VALUES (%s,%s,%s,%s,%s,%s)', batch)

    # --- tags (1,032 rows) ---
    print('  Inserting tags...')
    reader = read_csv(directory + 'tags.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),        # Id
            row[1],             # TagName
            to_int(row[2]),     # ExcerptPostId
            to_int(row[3]),     # WikiPostId
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO tags VALUES (%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO tags VALUES (%s,%s,%s,%s)', batch)

    # --- badges (79,851 rows) ---
    print('  Inserting badges...')
    reader = read_csv(directory + 'badges.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),    # Id
            int(row[1]),    # UserInfoId
            row[2],         # Name
            row[3],         # Date (ISO format)
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO badges VALUES (%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO badges VALUES (%s,%s,%s,%s)', batch)

    # --- postHistory (275,281 rows, multiline Text) ---
    print('  Inserting postHistory...')
    reader = read_csv(directory + 'postHistory.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),        # Id
            int(row[1]),        # PostHistoryTypeId
            int(row[2]),        # PostId
            row[3],             # CreationDate (ISO format)
            to_int(row[4]),     # UserInfoId
            to_str(row[5]) if len(row) > 5 else None,  # Text
            to_str(row[6]) if len(row) > 6 else None,  # Comment
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO postHistory VALUES (%s,%s,%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO postHistory VALUES (%s,%s,%s,%s,%s,%s,%s)', batch)

    # --- postLinks (11,102 rows) ---
    print('  Inserting postLinks...')
    reader = read_csv(directory + 'postLinks.csv')
    next(reader)
    batch = []
    for row in reader:
        batch.append((
            int(row[0]),    # Id
            row[1],         # CreationDate 
            int(row[2]),    # PostId
            int(row[3]),    # RelatedPostId
            int(row[4]),    # LinkTypeId
        ))
        if len(batch) >= BATCH_SIZE:
            flush(cursor, cnx, 'INSERT INTO postLinks VALUES (%s,%s,%s,%s,%s)', batch)
            batch = []
    flush(cursor, cnx, 'INSERT INTO postLinks VALUES (%s,%s,%s,%s,%s)', batch)

    cursor.close()
    cnx.close()


# Requirement4: add constraint (foreign key)
def requirement4(host, user, password):
    cnx = mysql.connector.connect(host=host, user=user, password=password)
    cursor = cnx.cursor()
    cursor.execute('SET GLOBAL innodb_buffer_pool_size=2*1024*1024*1024;')
    print('Adding constraints...')


    # TODO: WRITE CODE HERE
    cursor.execute('USE DMA_team15;')

    fk_queries = [
        'ALTER TABLE posts ADD FOREIGN KEY (OwnerUserId) REFERENCES users(UserId)',
        'ALTER TABLE question ADD FOREIGN KEY (PostId) REFERENCES posts(Id)',
        'ALTER TABLE question ADD FOREIGN KEY (AcceptedAnswerId) REFERENCES answer(Id)',
        'ALTER TABLE answer ADD FOREIGN KEY (PostId) REFERENCES posts(Id)',
        'ALTER TABLE answer ADD FOREIGN KEY (ParentId) REFERENCES question(Id)',
        'ALTER TABLE comments ADD FOREIGN KEY (PostId) REFERENCES posts(Id)',
        'ALTER TABLE comments ADD FOREIGN KEY (UserInfoId) REFERENCES users(UserId)',
        'ALTER TABLE votes ADD FOREIGN KEY (PostId) REFERENCES posts(Id)',
        'ALTER TABLE votes ADD FOREIGN KEY (UserInfoId) REFERENCES users(UserId)',
        'ALTER TABLE tags ADD FOREIGN KEY (ExcerptPostId) REFERENCES posts(Id)',
        'ALTER TABLE tags ADD FOREIGN KEY (WikiPostId) REFERENCES posts(Id)',
        'ALTER TABLE badges ADD FOREIGN KEY (UserInfoId) REFERENCES users(UserId)',
        'ALTER TABLE postHistory ADD FOREIGN KEY (PostId) REFERENCES posts(Id)',
        'ALTER TABLE postHistory ADD FOREIGN KEY (UserInfoId) REFERENCES users(UserId)',
        'ALTER TABLE postLinks ADD FOREIGN KEY (PostId) REFERENCES posts(Id)',
        'ALTER TABLE postLinks ADD FOREIGN KEY (RelatedPostId) REFERENCES posts(Id)',
    ]

    for query in fk_queries:
        cursor.execute(query)

    cnx.commit()
    cursor.close()
    cnx.close()


# TODO: REPLACE THE VALUES OF FOLLOWING VARIABLES
host = 'localhost'
user = 'root'
password = ''
directory_in = ''


requirement1(host=host, user=user, password=password)
requirement2(host=host, user=user, password=password)
requirement3(host=host, user=user, password=password, directory=directory_in)
requirement4(host=host, user=user, password=password)
print('Done!')
