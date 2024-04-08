<<<ADDING YOUR LAB>>>

Feel free to contribute your own labs, but follow the rules:

Lets assume you want to push lab named <lab_name> (f.e. "2.3.1").
Create a nickname (<your_nickname>). (mine is "Andrew"). You will use it every time.

1. Clone repo.
git clone git@gitlab.com:group-15380145/mipt_physics_labs.git
cd mipt_physics_labs

2. Create new branch named: "<lab_name>_<your_nickname>" and switch to it.
```git switch -c <lab_name>_<your_nickname>```

3. If <lab_name> folder does not exists, create it.

4. Create <lab_name>/<your_nickname> folder.

5. Put your lab files in <lab_name>/<your_nickname>.

6. Push <lab_name>_<your_nickname> branch to origin.
git push origin <lab_name>_<your_nickname>

7. In gitlab create MR (merge request) to branch main, give me (@Andrew-the-Programmer) the Reviewer role.

8. Wait untill I review and accept it.
