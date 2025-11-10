notes.md

I started with a runpod account and am going to follow each step, recording what happens

my balanmce is 13.33


try 1

i opened runpod and used secure cloud,  at  pod templates - selected Runpod pytorch  2.8.0
and went to pods selecting a40 (which was priced at 40 cents an hour)  and started the pod

I started  the web terminal  and followed the setup for runpod.setup.sh  which downloads lots of stuff

first bug-- it created two virtual envs (second one for ai tool kit) and it is downloading everything twice

B2: it is uninstalling things it installed and then reinstalling them

B3: is doing all the install before it creates the picture directory so i cannot upload images

runpod setup finished - al togoether the pod has be up 38 min  - lets fix these issues

try 2 - stopped the pod and terminated it   -  deployed it again This time i started jupyter lab

b4: still no directory for images , there is some confusion in the code about this   i want one dfirecrot ./photos that will hold the images and tabels

b5: quick_start.sh is not execuble

This time getting everything in place took 20 min
