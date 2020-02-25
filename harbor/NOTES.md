

# Poor LDAP integration

- Unable to have both local and ldap users

# Pain point 1

IMPORTANT: You can change the authentication mode from database to LDAP only if no local users have been added to the database. If there is at least one user other than admin in the Harbor database, you cannot change the authentication mode.
EVEN IF WE DELETE THIS USER

DEAD END

# Issue 1: 

- Create an first ldap account.
- Log in harbor with it
- Delete it in ldap
- Recreate another account with the same email than the deleted one.
- Try to log on, or to add this new user as a project member:  duplicate key value violates unique constraint "harbor_user_email_key"

Of course, there is no way to remove the old user from Harbor, which remains as Zombi.




  