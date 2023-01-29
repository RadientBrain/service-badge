# service-badge

- DB Used = `PostgreSQL`
- Command = `CREATE DATABASE badges`
- PostgreSQL URI = `postgresql://<username>:<password>@<host>:<port>/<db_name>`

- Table Name = `badges`

---

## | name | description | badge_file | eligible_students |

- File structure =

  ```
  service-badge
  │ README.md
  │ app.py
  │ .flaskenv
  │ .gitignore
  │ requirements.txt
  │
  └───static
  │ └───css
  │ │ └─── edit.css
  │ │ └─── main.css
  │ └───badges
  │
  └───templates
    └─── edit.html
    └─── index.html
    └─── list_badges.html
  ```

- Using the script:
  `chmod +x install.sh`
  `./install.sh`
