import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Step 1: Create the projects table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image TEXT NOT NULL,
        github_link TEXT
    )
''')

# Step 2: Comment this out if you don't want to add projects yet
# new_projects = [
#     ("Project One", "This is the first project.", "project1.png", "https://github.com/yourusername/project1"),
#     ("Project Two", "This is the second project.", "project2.png", "https://github.com/yourusername/project2")
# ]
# cursor.executemany('''
#     INSERT INTO projects (title, description, image, github_link)
#     VALUES (?, ?, ?, ?)
# ''', new_projects)

conn.commit()
conn.close()
