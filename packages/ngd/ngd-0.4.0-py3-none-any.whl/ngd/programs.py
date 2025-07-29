# Dictionary to store all program texts
program_texts = {
    1: """Go to the Documents folder:


cd ~/Documents
Create a new folder:


mkdir FirstProject
cd FirstProject
Create a new Python file:


nano hello.py
Inside hello.py, type:


print("Hello")
print("YourName, YourUSN")
Save the file: Press Ctrl+X, then Y, then Enter

▶️ (Optional) Run the Python File
If Python3 is installed:


python3 hello.py
If not:


sudo apt install python3
🗂️ Local Git Repository Setup
Initialize a new git repository:


git init
Check status (shows untracked files):


git status
Add Python file to staging area:


git add hello.py
Commit the file:


git commit -m "Initial commit"
Note: If you get a fatal error like:
fatal: unable to auto-detect email address

Set your name and email:


git config --global user.name "Your Name"
git config --global user.email "your@email.com"
Then try committing again.

🛠️ Basic Git Local Commands
To view commit logs:

git log
To check status:

git status
✅ Assessment Steps
Make some changes in hello.py (add/remove lines)

Check status:

git status
Check differences:


git diff
Add changes:


git add hello.py
Commit the changes:


git commit -m "Second commit"
Copy the commit ID from:

git log
Show details of the second commit:

git show <commit-id>
""",

    2: """ PUSH LOCAL TO REMOTE 

1. Push Local Repository to Remote Repository
Step 1: Create a remote repository
Go to GitHub

Click New Repository

Step 2: Copy the repository link
Example link:
https://github.com/YourUsername/YourRepo.git

Step 3: Add remote repository link to local Git

git remote add origin https://github.com/YourUsername/YourRepo.git
git remote -v 
Step 4: Push local repo to remote

git push -u origin master

You’ll be prompted to enter GitHub username and personal access token (in place of password).

Step 5: Refresh remote repo and check branch
Go to GitHub and check your code and branch.

2. Syncing Local and Remote Repositories
Step 1: Make changes in remote repo
On GitHub:
Edit a file and add a line like print("Hello from remote")

Step 2: Add commit message and commit
Use GitHub UI to write the commit message and confirm.

Step 3: Pull changes from remote

git pull origin master
Step 4: Check the local file
Open the file locally and confirm the changes.

Step 5: Git log

git log
Optional (Before merging remote changes):

git fetch origin
git diff master origin/master
git merge origin/master
3. Assignment Tasks
Task 1: Make changes in local repo and push to remote

# Edit a file, save it
git add .
git commit -m "Local change"
git push origin master
Task 2: Clone a public repository into a new folder

mkdir ~/Documents/gitlab2_clone
cd ~/Documents/gitlab2_clone
git clone https://github.com/someuser/somerepo.git
After cloning, check config:


cd somerepo
git remote -v
git branch -a
4. Branching
Step 1: Check all local branches

git branch
Step 2: Add a new branch

git branch test_branch
Step 3: Switch to the new branch

git checkout test_branch
Step 4: Make changes in test branch

# Edit file, add: print("Hello from test branch")
git add .
git commit -m "Added print in test_branch"
Step 5: Merge test branch into master

git checkout master
git merge test_branch
Step 6: Check file in master branch
Confirm the merged changes appear.

Step 7: Git log

git log
""",

    3: """Lab: Flask without Docker

Step 1. Create project folder
Open terminal and run:
cd ~/Documents
mkdir pythonproject
cd pythonproject
Step 2. Create app.py file
Inside pythonproject, create a file named app.py with the following code:
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home(name = None):
    return render_template('index.html', name = name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 

Step 3. Install Flask
In terminal, run:
pip install flask
Step 4. Create templates folder
Inside pythonproject, create a folder named templates:
mkdir templates
Step 5. Create index.html
Inside the templates folder, create a file named index.html with:
<!DOCTYPE html>
<html>
<head>
    <title>Flask App</title>
</head>
<body>
    <h1>Hello, Flask without Docker!</h1>
</body>
</html>
Step 6. Run the Flask app
In terminal, from inside pythonproject, run:
python app.py
Step 7. View in browser
Open your browser and go to:
http://127.0.0.1:5000/""",

    4: """Lab: Flask with Docker

    1. Create a Dockerfile
sandhya@ise-VirtualBox :~ $ cd Documents
sandhya@ise-VirtualBox :~ /Documents$ cd pythonproject
sandhya@ise-VirtualBox :~ /Documents/pythonproject$ ls
sandhya@ise-VirtualBox :~ /Documents/pythonproject$ nano Dockerfile

inside docker file :

FROM python:3-alpine3.15
WORKDIR /app
COPY . /app

RUN pip install flask

CMD ["python3", "app.py"]


2) docker build 

sudo docker build -t myimage:1 .

3) List all docker images 

sudo docker images 

4) docker run 

sudo docker run -p 8000:5000  myimage:1

5) check on port 8000
""",

    5: """JENKINS(CIE 1 PART )
START JENKINS 
sudo systemctl enable jenkins
sudo systemctl start Jenkins
sudo systemctl status jenkins

   go to port http://localhost:8080



1) SELECT NEW ITEM 
   type job name 
   select item type - Freestyle project 
   click OK 

2) In SCM section 
   add GitHub repo link : https://github.com/.....
    
3) Build Trigger Section 
   Build periodically 
    H/5****

4) Build Steps 
   Execute Shell 
     python3 hello.py


  apply and save , click build now then check build 
  also check branch on GitHub if its master or main 
""",

    6: """PROMETHEUS:

1) UPDATE PACKAGE 
    sudo apt-get update 


2: in home directory pull Prometheus image 

    sudo docker pull prom/prometheus 


3) go to documents ( cd documents)
      create new folder Prometheus(mkdir Prometheus)

       
  inside Prometheus.yml(cd prometheus , nano promethes/yml)
         
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']


4) Run Prometheus
   sudo docker run -d --name=prometheus \
>  -p 9090:9090 \
> -v ./prometheus.yml:/etc/prometheus/prometheus.yml \


5) go to http://localhost:9090

 promql 

prometheus_http_requests_total
rate(promeheus_http_requsts_total{handler="/api/v1/query"}[3m])

6) stop Prometheus 
    
  sudo docker stop prometheus


""",

    7: """GRAFANA

1) PULL GARFANA DOCKER IMAGES 

   sudo docker pull Grafana/Grafana

2) Run Grafana docker images 

   sudo docker run -d -p 3000:3000 --name=grafana grafana/grafana  

3) start Prometheus
    
    sudo docker start Prometheus


4) oprn browser at http://localhost:3000


5) go to dashboard , click on data sources  , then click on Prometheus , 

do ifconfig   and copy ip corresponding to 10.0.2.15
  

 in configuration add Prometheus server url 


4) in configuration change http method change to GET 

5) save & next 

6) click on dashboard -> create dashboard -> data sorces 

add query , RUN  and save dashboard 

7) sudo docker stop prometheus grafana
""",

    8: """DOCKER HUB PUSH IMAGE 

CRAETE DOCKER ACCOUNT AND RETRIEVE ACESS TOKEN 


1)RENAME DOCKER IMAGES 

    sudo docker images 

2) sudo docker tag myimage:1 docleruserid/dockerimage
   sudo docker images



3) LOGIN 

   sudo docker login -u dockeruserid

    add token from dockerhub 


4) sudo docker push dockeruser/dockerimage


5)  logout 
    docker logout 
""",

    9: """JENKINS (CIE2) 

CREATE JOB1 AS DONE IN CIE1 

1) type jobname and select freestyle 
       
2)  in build trigger select build after other project are built 
     in project to watch add git_job1(cie1)


3) select execute shell 
   echo $BUILD_NUMBER
   python3 -c "import datetime;  print(datetime.datetime.now())"


4) crete pipeline by 
    
     clicking on + icon 

     5) give pipline name 
          select build pipeline view 
       CREATE 

5) in build pipeline view title 
     add Title1
   select inintal job: git_job1
    freq : 60
    apply and save the run pipeline 
""",

    10: """DOCKER NETWORKING 

  1) curl -fssl https://get.docker.com -o get-docker.sh
  2) sudo sh get-docker.sh
   3) # docker network ls 
  4) sudo apt-get install bridge-utils
   5) sudo brctl show 


6) create container 
   sudo docker run -dt ubuntu bash 

7) # sudo docker run -dit --name c1 ubuntu 
     sudo docker run -dit --name c2 ubuntu


8) sudo docker network ls

9) sudo docker network inspect id OR [id]

10) sudo docker exec  -it c1 bash

11) apt update 

12) apt-get install iputils-ping  
13) ping ip of c2  
exit 


CUSTOM BRIDGE 

sudo docker network create custom_bridge

1) sudo docker run -dit --name c3 --network custom_bridge ubuntu

2)  sudo docker run -dit --name c4 --network custom_bridge ubuntu

3) sudo docker network inspect custom_bridge

4) sudo docker exec -it c3 bash

5) apt update, apt install iputils ping 

6) ping c2 fails but c4 will not fail 




CONNECTING DEFAULT BRIDGE TO CUSTOM BRIDGE 

1) Connecting container in default bridge to custom bridge
2)  Inspect the default bridge note down the container-id (C1) 2. Connect this container to custom bridge using following cmd 

docker network connect custom_bridge  c1 id 

brctl show


4) inspect custom bridge 

5)  Now get into the C1 container(default bridge) and ping c3 or c4  container(custom bridge) 

6)  To dissconnect connection
    docker network disconnect custom_bridge c1 id 

""",

    11: """KUBERNETES 


1. CREATE POD

kubectl run my-pod -- image=nginx -- restart=Never

kubectl get pods

Try to access nginx server (Through localhost or through ip address of pod)

   kubectl get pod my-pod -o wide


2. Expose your pod through NodePort Service

    kubectl expose pod my-pod --type=NodePort --port=80 --name=myservice

$ kubectl get services

$ minikube service my-service -- url

3) ACESS NGINX THROUGH IP ADRESS 


4) DELETE POD AND SERVICES 
    kubectl delete service my-service
     kubectl delete pod my-pod


   CREATE DEPLOYMENT REPLICA 

    kubectl create deployment my-deployment -- image=nginx -- replicas=2

$ kubectl get pods

kubectl get deployment

kubectl expose deployment my-deployment -- type=NodePort -- port=80

minikube service my-deployment

  minikube service my-deployment -- url


kubectl scale deployment my-deployment -- replicas=5

  kubectl get pods 

 kubectl delete pod mypod 
""",

    12: """12) Alert Dialog

kt:

package com.example.typeshit

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.support.v7.app.AlertDialog
import android.widget.Toast
import android.view.View

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    fun exit(view: View) {
        val alert = AlertDialog.Builder(this)
        alert.setTitle("Confirm Exit")
        alert.setIcon(R.drawable.warning)  // make sure you have warning.png or vector in drawable
        alert.setMessage("Are you sure you want to exit?")
        alert.setCancelable(false)

        alert.setPositiveButton("Yes") { _, _ ->
            finish()
        }

        alert.setNegativeButton("No") { _, _ ->
            Toast.makeText(this, "You clicked on No", Toast.LENGTH_LONG).show()
        }

        alert.setNeutralButton("Cancel") { _, _ ->
            Toast.makeText(this, "You clicked on Cancel", Toast.LENGTH_LONG).show()
        }

        alert.create().show()
    }
}


xml:

<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:paddingBottom="40dp"
    android:paddingLeft="40dp"
    android:paddingRight="40dp"
    android:paddingTop="40dp"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:onClick="exit"
        android:textStyle="normal|bold"
        style="@style/Widget.AppCompat.Button.Colored"
        android:layout_alignParentBottom="true"
        android:layout_centerHorizontal="true"
        android:layout_marginBottom="131dp"
        android:text="@string/exit" />

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginBottom="68dp"
        android:layout_above="@id/button"
        android:layout_centerHorizontal="true"
        android:textSize="18sp"
        android:textStyle="normal|bold"
        android:gravity="center"
        android:text="@string/click_over_button_to_exit" />
</RelativeLayout>

strings.xml:

<resources>
    <string name="app_name">typeshit</string>
    <string name="exit">Exit</string>
    <string name="click_over_button_to_exit">Click the button below to exit</string>
</resources>
""",

    13: """Progress Bar

xml:
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <ProgressBar
        android:id="@+id/progress_Bar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="200dp"
        android:layout_height="wrap_content"
        android:indeterminate="false"
        android:max="100"
        android:minWidth="200dp"
        android:minHeight="50dp"
        android:visibility="invisible"
        android:layout_centerHorizontal="true"
        android:layout_marginTop="100dp" />

    <TextView
        android:id="@+id/text_view"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_below="@id/progress_Bar"
        android:layout_centerHorizontal="true"
        android:layout_marginTop="20dp"
        android:text="0/100"
        android:textSize="18sp" />

    <Button
        android:id="@+id/show_button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_below="@id/text_view"
        android:layout_centerHorizontal="true"
        android:layout_marginTop="30dp"
        android:text="Start Progress" />

</RelativeLayout>

kt:
package com.example.typeshit

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView

class MainActivity : AppCompatActivity() {

    private lateinit var progressBar: ProgressBar
    private lateinit var txtView: TextView
    private var i = 0
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        progressBar = findViewById(R.id.progress_Bar)
        txtView = findViewById(R.id.text_view)
        val btn = findViewById<Button>(R.id.show_button)

        btn.setOnClickListener {
            progressBar.visibility = View.VISIBLE
            i = 0
            progressBar.progress = i

            Thread {
                while (i < 100) {
                    i += 1
                    handler.post {
                        progressBar.progress = i
                        txtView.text = "$i/${progressBar.max}"
                    }
                    try {
                        Thread.sleep(100)
                    } catch (e: InterruptedException) {
                        e.printStackTrace()
                    }
                }
                handler.post {
                    progressBar.visibility = View.INVISIBLE
                }
            }.start()
        }
    }
}

""",

    14: """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:gravity="center">

    <!-- TextView to show current progress -->
    <TextView
        android:id="@+id/progress_value"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Progress: 0"
        android:textSize="18sp"
        android:layout_marginBottom="20dp"/>

    <!-- SeekBar -->
    <SeekBar
        android:id="@+id/seek_bar"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:max="100" />
</LinearLayout>

kt:

package com.example.typeshit

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.SeekBar
import android.widget.TextView

class MainActivity : AppCompatActivity() {

    private lateinit var seekBar: SeekBar
    private lateinit var progressText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        seekBar = findViewById(R.id.seek_bar)
        progressText = findViewById(R.id.progress_value)

        seekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                progressText.text = "Progress: $progress"
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {
                // Optional: handle when user starts dragging
            }

            override fun onStopTrackingTouch(seekBar: SeekBar?) {
                // Optional: handle when user stops dragging
            }
        })
    }
}
""",

    15: """14) Canva:

kt:

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.ShapeDrawable
import android.graphics.drawable.shapes.OvalShape
import android.graphics.drawable.shapes.RectShape
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.ImageView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val bitmap: Bitmap = Bitmap.createBitmap(700, 1000,
            Bitmap.Config.ARGB_8888)
        val canvas: Canvas = Canvas(bitmap)
        var shapeDrawable: ShapeDrawable
// rectangle positions
        var left = 100
        var top = 100
        var right = 600
        var bottom = 400

// draw rectangle shape to canvas
        shapeDrawable = ShapeDrawable(RectShape())
        shapeDrawable.setBounds( left, top, right, bottom)
        shapeDrawable.getPaint().setColor(Color.parseColor("#009944"))
        shapeDrawable.draw(canvas)
// draw oval shape to canvas
        shapeDrawable = ShapeDrawable(OvalShape())
        shapeDrawable.setBounds( 100, 500, 600, 800)
        shapeDrawable.getPaint().setColor(Color.parseColor("#009191"))
        shapeDrawable.draw(canvas)
        val iv = findViewById<ImageView>(R.id.imageV)
// now bitmap holds the updated pixels
// set bitmap as background to ImageView

        val pCircle = Paint()
        pCircle.setColor(Color.BLACK)
        canvas.drawCircle(30f, 30f, 30f, pCircle)
        val pBackground = Paint()
        pBackground.color = Color.RED
        canvas.drawRect(450f, 450f, 500f, 500f, pBackground)
        iv.background = BitmapDrawable(getResources(), bitmap)
    }
}

xml:

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <ImageView
        android:id="@+id/imageV"
        android:layout_width="315dp"
        android:layout_height="526dp"
        android:layout_marginTop="100dp"
        android:layout_marginEnd="50dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</android.support.constraint.ConstraintLayout>""",

    16: """14)ANIMATION

res → New → Android Resource Directory
Resource type: anim
Directory name: anim (it auto-fills)

anim folder → New → Animation Resource File
Enter a name, e.g., fade_in.xml

bounce.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
        <translate
            android:fromYDelta="100%"
            android:toYDelta="-20%"
            android:duration="300" />
        <translate
            android:startOffset="500"
            android:fromYDelta="-20%"
            android:toYDelta="10%"
            android:duration="150" />
        <translate
            android:startOffset="1000"
            android:fromYDelta="10%"
            android:toYDelta="0"
            android:duration="100" />
</set>


fad_in.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <alpha
        android:duration="1000"
        android:fromAlpha="0.1"
        android:toAlpha="1.0" />
</set>


fade_out.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <alpha
        android:duration="2000"
        android:fillAfter="true"
        android:fromAlpha="1.0"
        android:toAlpha="0.1" />
</set>

slide_down.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <translate
        android:duration="1000"
        android:fromYDelta="-100%"
        android:toYDelta="0" />
</set>



slide_up.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <translate
        android:duration="1000"
        android:fromYDelta="100%"
        android:toYDelta="0" />
</set>


zoom_in.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <scale
        android:duration="1000"
        android:fromXScale="1"
        android:fromYScale="1"
        android:pivotX="50%"
        android:pivotY="50%"
        android:toXScale="1.5"
        android:toYScale="1.5" />
</set>



zoom_out.xml:
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <scale
        android:duration="1000"
        android:fromXScale="1.0"
        android:fromYScale="1.0"
        android:pivotX="50%"
        android:pivotY="50%"
        android:toXScale="0.5"
        android:toYScale="0.5" />
</set>



activity_main.xml:
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/textView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:layout_above="@+id/linearLayout"
        android:gravity="center"
        android:text="Mobile Application Development"
        android:textSize="32sp"
        android:textColor="@color/teal_200"
        android:textStyle="bold" />

    <LinearLayout
        android:id="@+id/linearLayout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_alignParentBottom="true"
        android:orientation="vertical">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2">

            <Button
                android:id="@+id/fade_in"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Fade In"
                android:textAllCaps="false" />

            <Button
                android:id="@+id/fade_out"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Fade Out"
                android:textAllCaps="false" />
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2">

            <Button
                android:id="@+id/zoom_in"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Zoom In"
                android:textAllCaps="false" />

            <Button
                android:id="@+id/zoom_out"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Zoom Out"
                android:textAllCaps="false" />
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2">

            <Button
                android:id="@+id/slide_down"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Slide Down"
                android:textAllCaps="false" />

            <Button
                android:id="@+id/slide_up"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Slide Up"
                android:textAllCaps="false" />
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2">

            <Button
                android:id="@+id/bounce"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Bounce"
                android:textAllCaps="false" />

            <Button
                android:id="@+id/rotate"
                android:layout_width="0dp"
                android:layout_height="match_parent"
                android:layout_weight="1"
                android:text="Rotate"
                android:textAllCaps="false" />
        </LinearLayout>

    </LinearLayout>


</RelativeLayout>





MainActivity.kt:
package com.example.animation

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.view.animation.AnimationUtils
import android.widget.Button
import android.widget.TextView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val textView = findViewById<TextView>(R.id.textView)

        findViewById<Button>(R.id.fade_in).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.fad_in)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.fade_out).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.fade_out)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.zoom_in).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.zoom_in)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.zoom_out).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.zoom_out)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.slide_up).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.slide_up)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.slide_down).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.slide_down)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.bounce).setOnClickListener {
            val animation = AnimationUtils.loadAnimation(this, R.anim.bounce)
            textView.startAnimation(animation)
        }

        findViewById<Button>(R.id.rotate).setOnClickListener {
            textView.animate().apply {
                duration = 1000
                rotationXBy(360f)
            }.start()
        }
    }
}

""",

    17: """15)Options menu

Right-click res → New → Android Resource Directory → Choose menu as the
Resource type.
• Create a new XML menu file:
• Right-click the menu folder → New → Menu Resource File → Name it
menu_main.xml.

menu_main.xml:

<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <item
        android:id="@+id/overflowMenu"
        android:icon="@drawable/menu"
        android:title=""
        app:showAsAction="always">
        <menu>
            <item
                android:id="@+id/settings"
                android:icon="@drawable/setting"
                android:title="SETTINGS"
                app:showAsAction="never" />
            <item
                android:id="@+id/about"
                android:icon="@drawable/about"
                android:title="ABOUT"
                app:showAsAction="never" />
            <item
                android:id="@+id/exit"
                android:icon="@drawable/exit"
                android:title="EXIT"
                app:showAsAction="never" />
        </menu>
    </item>
</menu>



activity_main.xml:

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</android.support.constraint.ConstraintLayout>


MainActivity.kt:
package com.example.menu

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_main,menu)
        return super.onCreateOptionsMenu(menu)
    }
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId){
            R.id.about -> Toast.makeText(this,"About Selected",Toast.LENGTH_SHORT).show()
            R.id.settings -> Toast.makeText(this,"Settings Selected",Toast.LENGTH_SHORT).show()
            R.id.exit -> Toast.makeText(this,"Exit Selected",Toast.LENGTH_SHORT).show()
        }
        return super.onOptionsItemSelected(item)
    }
}
""",

    18: """16) CONTEXT MENU

menu_main.xml:
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <item android:id="@+id/item1"
        android:title="Open"
        app:showAsAction="never"
        />
    <item android:id="@+id/item2"
        android:title="Search"
        app:showAsAction="never"
        />
    <item android:id="@+id/item3"
        android:title="Exit"
        app:showAsAction="never"
        />
</menu>


activity_main.xml:
<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/B1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Context Menu"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</android.support.constraint.ConstraintLayout>

MainActivity.kt:
package com.example.menu

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.support.v7.widget.PopupMenu
import android.view.ContextMenu
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Button
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val B1 = findViewById<Button>(R.id.B1)
        registerForContextMenu(B1)
        B1.setOnClickListener { v -> openContextMenu(v)}
    }
    override fun onCreateContextMenu(
        menu: ContextMenu?,
        v: View?,
        menuInfo: ContextMenu.ContextMenuInfo?
    ) {
        super.onCreateContextMenu(menu, v, menuInfo)
        menuInflater.inflate(R.menu.menu_main,menu)
    }
    override fun onContextItemSelected(item: MenuItem): Boolean {
        when (item.itemId){
            R.id.item1 -> Toast.makeText(this,"Open Selected",Toast.LENGTH_SHORT).show()
            R.id.item2 -> Toast.makeText(this,"Search Selected",Toast.LENGTH_SHORT).show()
            R.id.item3 -> Toast.makeText(this,"Exit Selected",Toast.LENGTH_SHORT).show()
        }
        return super.onContextItemSelected(item)
    }
}

""",

    19: """POPUP MENU

menu_main.xml:
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <item android:id="@+id/item1"
        android:title="Open"
        app:showAsAction="never"
        />
    <item android:id="@+id/item2"
        android:title="Search"
        app:showAsAction="never"
        />
    <item android:id="@+id/item3"
        android:title="Exit"
        app:showAsAction="never"
        />
</menu>

activity_main.xml:
<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/B1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Popup menu"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</android.support.constraint.ConstraintLayout>


MainActivity.kt:
package com.example.menu

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.support.v7.widget.PopupMenu
import android.view.Menu
import android.view.MenuItem
import android.widget.Button
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val B1 = findViewById<Button>(R.id.B1)
        B1.setOnClickListener {
            val popupMenu: PopupMenu = PopupMenu(this, B1)
            popupMenu.menuInflater.inflate(R.menu.menu_main, popupMenu.menu)

            // 02-05-2025 Rashmi R, iSE 23 (This line appears to be a comment/note, not code)

            popupMenu.setOnMenuItemClickListener(PopupMenu.OnMenuItemClickListener { item ->
                when (item.itemId) {
                    R.id.item1 ->
                        Toast.makeText(
                            this@MainActivity,
                            "You Clicked : " + item.title,
                            Toast.LENGTH_SHORT
                        ).show()
                    R.id.item2 ->
                        Toast.makeText(
                            this@MainActivity,
                            "You Clicked : " + item.title,
                            Toast.LENGTH_SHORT
                        ).show()
                    R.id.item3 ->
                        Toast.makeText(
                            this@MainActivity,
                            "You Clicked : " + item.title,
                            Toast.LENGTH_SHORT
                        ).show()
                }
                true
            })
            popupMenu.show()
        }
    }
}
""",

    20: """17)Fragments

Right-click > New > Fragment > Fragment (Blank) in java > your.package.name

main kt:

package com.example.exam

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.support.v4.app.Fragment
import android.support.v4.app.FragmentManager
import android.widget.Button

@Suppress("DEPRECATION")
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
//        lateinit var fragmentManager: FragmentManager
        var blueButton = findViewById<Button>(R.id.blueButton);
        var yellowButton = findViewById<Button>(R.id.yellowButton);
//        fragmentManager = getSupportFragmentManager();

        blueButton.setOnClickListener {
            loadFragment(fragment_1())
        }

        yellowButton.setOnClickListener {
            loadFragment(fragment_2())
        }
    }

    private fun loadFragment(fragment: Fragment) {
        // Use supportFragmentManager directly
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragmentContainer, fragment)
            .addToBackStack(null)
            .commit()
    }
}

main_xml:

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <FrameLayout
        android:id="@+id/fragmentContainer"
        android:layout_width="410dp"
        android:layout_height="399dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent">

    </FrameLayout>

    <Button
        android:id="@+id/blueButton"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="56dp"
        android:layout_weight="1"
        android:text="Fragment 1"
        android:backgroundTint="#2196F3"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/fragmentContainer"
        tools:ignore="ExtraText" />

    <Button
        android:id="@+id/yellowButton"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="56dp"
        android:layout_weight="1"
        android:text="Fragment 2"
        android:backgroundTint="#FFEB3B"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/fragmentContainer" />

</android.support.constraint.ConstraintLayout>

fragment_1 kt:

package com.example.exam

import android.os.Bundle
import android.support.v4.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup

// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [fragment_1.newInstance] factory method to
 * create an instance of this fragment.
 */
class fragment_1 : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_1, container, false)
    }
}

fragment_1 xml:

<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#2196F3"
    tools:context=".fragment_1">

    <!-- TODO: Update blank fragment layout -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="@string/hello_blank_fragment" />

</FrameLayout>

fragment_2 kt:

package com.example.exam

import android.os.Bundle
import android.support.v4.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup

private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

class fragment_2 : Fragment() {
    // TODO: Rename and change types of parameters
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_2, container, false)
    }
}

fragment_2 xml:

<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#FFEB3B"
    tools:context=".fragment_2">

    <!-- TODO: Update blank fragment layout -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="@string/hello_blank_fragment" />

</FrameLayout>
""",

    21: """Database

right click your package (com.example.database) -> new -> kotlin class/file -> file -> Databasehelper.kt


layout->dialog_update_student.xml

main kt:

package com.example.exam2

import DatabaseHelper
import android.content.DialogInterface
import android.database.Cursor
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.support.v7.app.AlertDialog
import android.view.LayoutInflater
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import com.example.exam2.R

class MainActivity : AppCompatActivity() {

    private lateinit var etFirstName: EditText
    private lateinit var etLastName: EditText
    private lateinit var btnAddStudent: Button
    private lateinit var btnDeleteStudent: Button
    private lateinit var btnUpdateStudent: Button
    private lateinit var btnListStudents: Button
    private lateinit var databaseHelper: DatabaseHelper

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etFirstName = findViewById(R.id.et_firstName)
        etLastName = findViewById(R.id.et_lastName)
        btnAddStudent = findViewById(R.id.btn_addStudent)
        btnDeleteStudent = findViewById(R.id.btn_deleteStudent)
        btnUpdateStudent = findViewById(R.id.btn_updateStudent)
        btnListStudents = findViewById(R.id.btn_listStudents)

        databaseHelper = DatabaseHelper(this)

        // Add Student
        btnAddStudent.setOnClickListener {
            val firstName = etFirstName.text.toString().trim()
            val lastName = etLastName.text.toString().trim()

            if (firstName.isEmpty() || lastName.isEmpty()) {
                Toast.makeText(this, "Please enter both First Name and Last Name", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (databaseHelper.addStudent(firstName, lastName)) {
                Toast.makeText(this, "Student added successfully!", Toast.LENGTH_SHORT).show()
                etFirstName.text.clear()
                etLastName.text.clear()
            } else {
                Toast.makeText(this, "Failed to add student. Maybe student already exists or an error occurred.", Toast.LENGTH_SHORT).show()
            }
        }

        // Delete Student
        btnDeleteStudent.setOnClickListener {
            val firstName = etFirstName.text.toString().trim()

            if (firstName.isEmpty()) {
                Toast.makeText(this, "Please enter the First Name to delete", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (databaseHelper.deleteStudent(firstName)) {
                Toast.makeText(this, "Student deleted successfully!", Toast.LENGTH_SHORT).show()
                etFirstName.text.clear()
                etLastName.text.clear()
            } else {
                Toast.makeText(this, "Failed to delete student. Student not found or an error occurred.", Toast.LENGTH_SHORT).show()
            }
        }

        // Update Student
        btnUpdateStudent.setOnClickListener {
            val oldFirstName = etFirstName.text.toString().trim()

            if (oldFirstName.isEmpty()) {
                Toast.makeText(this, "Please enter the First Name of the student to update", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (!databaseHelper.studentExists(oldFirstName)) {
                Toast.makeText(this, "Student with this First Name does not exist.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Show an alert dialog to get the new name
            val builder = AlertDialog.Builder(this)
            builder.setTitle("Update Student Name")

            // Set up the input fields
            val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_update_student, null)
            val newFirstNameEt = dialogView.findViewById<EditText>(R.id.et_newFirstName)
            val newLastNameEt = dialogView.findViewById<EditText>(R.id.et_newLastName)
            builder.setView(dialogView)

            // Set up the buttons
            builder.setPositiveButton("Update") { dialog: DialogInterface, _: Int ->
                val newFirstName = newFirstNameEt.text.toString().trim()
                val newLastName = newLastNameEt.text.toString().trim()

                if (newFirstName.isEmpty() || newLastName.isEmpty()) {
                    Toast.makeText(this, "New First Name and Last Name cannot be empty.", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }

                if (databaseHelper.updateStudent(oldFirstName, newFirstName, newLastName)) {
                    Toast.makeText(this, "Student updated successfully!", Toast.LENGTH_SHORT).show()
                    etFirstName.text.clear()
                    etLastName.text.clear()
                } else {
                    Toast.makeText(this, "Failed to update student. An error occurred.", Toast.LENGTH_SHORT).show()
                }
            }
            builder.setNegativeButton("Cancel") { dialog: DialogInterface, _: Int ->
                dialog.cancel()
            }

            builder.show()
        }

        // List Students
        btnListStudents.setOnClickListener {
            val res = databaseHelper.getAllStudents()
            if (res == null || res.count == 0) {
                // Show message
                showMessage("Error", "No students found")
                return@setOnClickListener
            }

            val buffer = StringBuffer()
            while (res.moveToNext()) {
                buffer.append("ID: ${res.getString(0)}\n")
                buffer.append("First Name: ${res.getString(1)}\n")
                buffer.append("Last Name: ${res.getString(2)}\n\n")
            }

            // Show all data
            showMessage("Student Data", buffer.toString())
            res.close() // Close the cursor
        }
    }

    private fun showMessage(title: String, message: String) {
        val builder = AlertDialog.Builder(this)
        builder.setCancelable(true)
        builder.setTitle(title)
        builder.setMessage(message)
        builder.show()
    }
}

Databasehelper.kt

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import android.util.Log

class DatabaseHelper(context: Context) :
    SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        private const val DATABASE_NAME = "StudentDB.db"
        private const val DATABASE_VERSION = 1

        const val TABLE_STUDENTS = "students"
        const val COL_ID = "id"
        const val COL_FIRST_NAME = "first_name"
        const val COL_LAST_NAME = "last_name"

        // SQL query to create the table
        private const val CREATE_TABLE_STUDENTS =
            "CREATE TABLE $TABLE_STUDENTS (" +
                    "$COL_ID INTEGER PRIMARY KEY AUTOINCREMENT," +
                    "$COL_FIRST_NAME TEXT," +
                    "$COL_LAST_NAME TEXT" +
                    ")"
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(CREATE_TABLE_STUDENTS)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Drop older table if existed
        db.execSQL("DROP TABLE IF EXISTS $TABLE_STUDENTS")
        // Create tables again
        onCreate(db)
    }

    // --- CRUD Operations ---

    // Add a new student
    fun addStudent(firstName: String, lastName: String): Boolean {
        val db = this.writableDatabase
        val values = ContentValues().apply {
            put(COL_FIRST_NAME, firstName)
            put(COL_LAST_NAME, lastName)
        }

        val result = db.insert(TABLE_STUDENTS, null, values)
        db.close()
        return result != -1L // Returns true if data inserted successfully, false otherwise
    }

    // Delete a student by first name
    fun deleteStudent(firstName: String): Boolean {
        val db = this.writableDatabase
        val result = db.delete(
            TABLE_STUDENTS,
            "$COL_FIRST_NAME = ?",
            arrayOf(firstName)
        )
        db.close()
        return result > 0 // Returns true if one or more rows were deleted
    }

    // Update a student's name
    fun updateStudent(oldFirstName: String, newFirstName: String, newLastName: String): Boolean {
        val db = this.writableDatabase
        val values = ContentValues().apply {
            put(COL_FIRST_NAME, newFirstName)
            put(COL_LAST_NAME, newLastName)
        }

        val result = db.update(
            TABLE_STUDENTS,
            values,
            "$COL_FIRST_NAME = ?",
            arrayOf(oldFirstName)
        )
        db.close()
        return result > 0 // Returns true if one or more rows were updated
    }

    // Get all students
    fun getAllStudents(): Cursor? {
        val db = this.readableDatabase
        return db.rawQuery("SELECT * FROM $TABLE_STUDENTS", null)
    }

    // Check if a student exists by first name
    fun studentExists(firstName: String): Boolean {
        val db = this.readableDatabase
        val cursor = db.query(
            TABLE_STUDENTS,
            arrayOf(COL_ID),
            "$COL_FIRST_NAME = ?",
            arrayOf(firstName),
            null, null, null
        )
        val exists = cursor.count > 0
        cursor.close()
        db.close()
        return exists
    }
}

dailog_update_student.xml:

<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <EditText
        android:id="@+id/et_newFirstName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="New First Name"
        android:inputType="textPersonName"
        android:layout_marginBottom="8dp"/>

    <EditText
        android:id="@+id/et_newLastName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="New Last Name"
        android:inputType="textPersonName"/>

</LinearLayout>

main.xml:

<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <EditText
        android:id="@+id/et_firstName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="First Name"
        android:inputType="textPersonName"
        android:layout_marginBottom="8dp"/>

    <EditText
        android:id="@+id/et_lastName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Last Name"
        android:inputType="textPersonName"
        android:layout_marginBottom="16dp"/>

    <Button
        android:id="@+id/btn_addStudent"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="ADD STUDENT"
        android:layout_marginBottom="8dp"/>

    <Button
        android:id="@+id/btn_deleteStudent"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="DELETE STUDENT"
        android:layout_marginBottom="8dp"/>

    <Button
        android:id="@+id/btn_updateStudent"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="UPDATE STUDENT"
        android:layout_marginBottom="8dp"/>

    <Button
        android:id="@+id/btn_listStudents"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="LIST STUDENTS"/>


</LinearLayout>
""",

22: """Shared_pref1

kt:
package com.example.sharedpref

import android.content.Context
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val name = findViewById<EditText>(R.id.ed1)
        val password = findViewById<EditText>(R.id.ed2)
        val save = findViewById<Button>(R.id.b1)
        val load = findViewById<Button>(R.id.b2)
        val del = findViewById<Button>(R.id.b4)

        // Instantiate SharedPreferences
        val sharedPref = getSharedPreferences("addName", Context.MODE_PRIVATE)
        val edit = sharedPref.edit()

        // Save data
        save.setOnClickListener {
            edit.putString("name", name.text.toString())
            edit.putString("password", password.text.toString())
            edit.commit()
            Toast.makeText(this, "Data Saved", Toast.LENGTH_LONG).show()
        }

        // Load data
        load.setOnClickListener {
            val getName = sharedPref.getString("name", "default value")
            val getPass = sharedPref.getString("password", "default value")
            Toast.makeText(this, "$getName $getPass", Toast.LENGTH_LONG).show()
        }

        // Delete data
        del.setOnClickListener {
            edit.clear()
            edit.commit()
            Toast.makeText(this, "Data Cleared", Toast.LENGTH_SHORT).show()
        }
    }
}

xml:

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">
    <EditText
        android:id="@+id/ed1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="56dp"
        android:ems="10"
        android:hint="Username"
        android:inputType="textPersonName"
        android:minHeight="48dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.497"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <EditText
        android:id="@+id/ed2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="36dp"
        android:ems="10"
        android:hint="Password"
        android:inputType="textPersonName"
        android:minHeight="48dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.497"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/ed1" />

    <Button
        android:id="@+id/b1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="95dp"
        android:text="Save"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.235"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/ed2" />
    <Button
        android:id="@+id/b2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginStart="96dp"
        android:layout_marginTop="95dp"
        android:text="Load"
        app:layout_constraintStart_toEndOf="@+id/b1"
        app:layout_constraintTop_toBottomOf="@+id/ed2" />
    <Button
        android:id="@+id/b4"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="20dp"
        android:layout_marginEnd="68dp"
        android:text="DELETE"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/b2" />
</android.support.constraint.ConstraintLayout>
""",
23: """shared_pref2:

xml:

<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity"
    tools:ignore="HardcodedText">

    <TextView
        android:id="@+id/textview"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_centerHorizontal="true"
        android:layout_marginTop="32dp"
        android:text="Shared Preferences"
        android:textColor="@android:color/black"
        android:textSize="24sp" />

    <EditText
        android:id="@+id/ed1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_below="@id/textview"
        android:layout_marginStart="16dp"
        android:layout_marginTop="16dp"
        android:layout_marginEnd="16dp"
        android:hint="Enter your Name"
        android:padding="10dp" />

    <EditText
        android:id="@+id/ed2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_below="@id/ed1"
        android:layout_marginStart="16dp"
        android:layout_marginTop="16dp"
        android:layout_marginEnd="16dp"
        android:hint="Enter your Age"
        android:inputType="number"
        android:padding="10dp" />



</RelativeLayout>

kt:

package com.example.exam3

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.EditText


class MainActivity : AppCompatActivity() {

    private lateinit var name: EditText
    private lateinit var age: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        name = findViewById(R.id.ed1)
        age = findViewById(R.id.ed2)
    }

    // Fetch the stored data in onResume()
    // Because this is what will be called when the app opens again
    override fun onResume() {
        super.onResume()

        // Fetching the stored data from SharedPreferences
        val sh = getSharedPreferences("MySharedPref", MODE_PRIVATE)

        val s1 = sh.getString("name", "")
        val a = sh.getInt("age", 0)

        // Setting the fetched data in the EditTexts
        name.setText(s1)
        age.setText(a.toString())
    }

    // Store the data in SharedPreferences in the onPause()
    // This method is called when the user closes the application
    override fun onPause() {
        super.onPause()

        // Creating a SharedPreferences object
        val sharedPreferences = getSharedPreferences("MySharedPref", MODE_PRIVATE)
        val myEdit = sharedPreferences.edit()

        // Writing user data to SharedPreferences
        myEdit.putString("name", name.text.toString())

        // Safely parsing age input
        val ageText = age.text.toString()
        val ageInt = ageText.toIntOrNull() ?: 0
        myEdit.putInt("age", ageInt)

        // Applying changes
        myEdit.apply()
    }
}
""",
24: """Explicit & implicit 1

java>new>activity

MainActiviy.kt:

package com.example.explicitintents

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Explicit Intent
        val explicitButton = findViewById<Button>(R.id.ExplicitButton)
        explicitButton.setOnClickListener {
            Toast.makeText(this, "Explicit Intent", Toast.LENGTH_SHORT).show()
            val explicitIntent = Intent(this, SecondActivity::class.java)
            startActivity(explicitIntent)
        }

        // Implicit Intent
        val url = "https://www.google.com"
        val ib = findViewById<Button>(R.id.B1)
        ib.setOnClickListener {
            val implicitIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            startActivity(implicitIntent)
        }
    }
}

activity_main.xml

<?xml version="1.0" encoding="utf-8"?>
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/ExplicitButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginVertical="400dp"
        android:layout_marginTop="88dp"
        android:text="Explicit Intents"
        android:textAllCaps="true"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.455"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />


    <Button
        android:id="@+id/B1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="40dp"
        android:layout_marginEnd="144dp"
        android:text="Implicit Intents"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/ExplicitButton" />

</android.support.constraint.ConstraintLayout>

SecondActivity.kt:

package com.example.explicitintents

import android.content.Intent
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class SecondActivity:AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)

//Explicit Intent

    }
}

activity_second.xml:

<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".secondactivity">
    <TextView
        android:id="@+id/resultTv"
        android:textSize="30sp"
        android:textStyle="bold"
        android:text="helllo"
        android:textColor="#000"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>

mainfest.xml:
<activity
            android:name=".SecondActivity"
            android:exported="false" />
""",

25: """intent2

MainActivity.kt:

package com.example.msg

import android.content.Intent
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val nameEt = findViewById<EditText>(R.id.nameEt)
        val emailEt = findViewById<EditText>(R.id.emailEt)
        val phoneEt = findViewById<EditText>(R.id.phoneEt)
        val saveBtn = findViewById<Button>(R.id.saveBtn)

        saveBtn.setOnClickListener {
            val name = nameEt.text.toString()
            val email = emailEt.text.toString()
            val phone = phoneEt.text.toString()

            val intent = Intent(this, SecondActivity::class.java)
            intent.putExtra("Name", name)
            intent.putExtra("Email", email)
            intent.putExtra("Phone", phone)
            startActivity(intent)
        }
    }
}

activity_main.xml:

<?xml version="1.0" encoding="utf-8"?>

<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <EditText
        android:id="@+id/nameEt"
        android:hint="Enter Name"
        android:inputType="text"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <EditText
        android:id="@+id/emailEt"
        android:hint="Enter Email"
        android:inputType="textEmailAddress"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <EditText
        android:id="@+id/phoneEt"
        android:hint="Enter Phone"
        android:inputType="phone"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <Button
        android:id="@+id/saveBtn"
        android:text="Save"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />

</LinearLayout>

SecondActivity.kt:

package com.example.msg

import android.content.Intent
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.TextView

class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)
//get data from intent
        val intent = intent
        val name = intent.getStringExtra("Name")
        val email = intent.getStringExtra("Email")
        val phone = intent.getStringExtra("Phone")
//textview
        val resultTv = findViewById<TextView>(R.id.resultTv)
//setText
        resultTv.text = "Name: "+name+"\nEmail: "+email+"\nPhone: "+phone
    }
}

activity_second.xml:

<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".SecondActivity">
    <TextView
        android:id="@+id/resultTv"
        android:textSize="30sp"
        android:textStyle="bold"
        android:textColor="#000"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>

manifest :
<activity
            android:name=".SecondActivity"
            android:exported="false" />
"""


}

def print_program(program_number):
    """
    Print the text of a specific program.
    
    Args:
        program_number (int): The number of the program to print (1-21)
    """
    if program_number not in program_texts:
        print(f"Error: Program {program_number} not found. Available programs are 1-21.")
        return
    
    print(program_texts[program_number]) 