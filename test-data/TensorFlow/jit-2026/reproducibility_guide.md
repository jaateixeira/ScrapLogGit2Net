
How did we get the networks for the paper we submit ? 

= Get a clone of the TensorFLow repository ==  

The first step is to get a clone of the Tensor Flow repository  

```
$ git clone https://github.com/tensorflow/tensorflow.git
```

Then you need to get the logs with 
```
git log --pretty=format:"==%an;%ae;%ad==" --name-only 
```

We did it using [1-get-raw-inputs-all.sh](1-get-raw-inputs-all.sh)


On 24 Jan, we ran our last analysis 
Output will be saved to: ../raw-inputs/tensorflow_2026-01-24_all.IN.TXT




But then it should be done year by year 
```
git log --since='Apr 1 2021' --until='Apr 4 2021' --pretty=format:"==%an;%ae;%ad==" --name-only
```

We did it using[1-get-raw-inputs-yearly.sh](1-get-raw-inputs-yearly.sh)