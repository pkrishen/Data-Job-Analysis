import sqlite3

#Create sqlite tables
conn = sqlite3.connect('JobData.db')

c = conn.cursor()

c.execute(""" CREATE TABLE Jobs(
    id text not null,
    job_title text not null,
    company text not null,
    location text not null,
    rating_provided text not null,
    rating real null,
    salary_provided text not null,
    weblink text not null,
    date_recorded not null, 
    location_model text, 
    jurisdiction text, 
    city text, 
    country text,

    CONSTRAINT PK_Jobs_id PRIMARY KEY (id)
)
""")

c.execute(""" CREATE TABLE Salaries(
    id text not null,
    salary_text text not null,
    salary_type text null,
    salary_period text null,
    floor real null,
    expected real null,
    ceiling real null,

    CONSTRAINT PK_Salaries_id PRIMARY KEY (id),
    CONSTRAINT FK_Salaries_id FOREIGN KEY (id) REFERENCES Jobs (id)
)
""")

c.execute(""" CREATE TABLE KeywordRef(
    id text not null,
    keyword text not null,
    CONSTRAINT PK_KeywordRef_id_keyword PRIMARY KEY (id, keyword)
)
""")

conn.commit()

conn.close()