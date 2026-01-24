
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

