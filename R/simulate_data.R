library(tidyverse)
library(brms)

# Creating Simulated Data
# In order to build and test our model in brms, we must first create a simulated data set that is similar to our actual experiment data. This allows us to confirm the brms model is working and successfully recovers the parameters we set before applying it to our real experimental data that has unknown parameter values. In the actual data, there will be many group-wise differences in location and scale parameters. The following simulated data only has explicit differences between the $\eta$ (location) of the two age groups (older vs younger).

generate_conditions_both_labs<- function(numSubjects,trialsPerCondition,targetNumConds,speedsPerCond) {
  #e.g.:
  #numSubjects<- 50
  #trialsPerCondition<- 5
  #targetNumConds<- c(2,3)
  #Array of speeds (not very realistic because mostly controlled by a staircase in actual experiment)
  #speeds<-seq(.02,1.8, length.out = 12) # trials at 12 different speeds between .02 and 1.8
  
  #Generate data frame for simulated data
  sim_conditions <- tidyr::expand_grid(
    subj = seq(1, numSubjects), #subjects
    rep = seq(1,trialsPerCondition), #replicates of each trial combination
    num_target = targetNumConds, #number of targets particpant tracks
    speed = speeds
  )
  
  #Assign half of subjects to each lab, and set gender and age for each subject
  sim_conditions <- sim_conditions %>%
    group_by(subj) %>%
    mutate(
      gender = sample(c("M","F"), 1, replace = TRUE),
      age_group = sample(c("younger", "older"), 1, replace = TRUE),
      lab = sample(c("rf", "holcombe"), 1, replace = TRUE) 
    ) %>% ungroup()
  
  # Set number of objects per ring based on lab
  sim_conditions <- sim_conditions %>%
    mutate(
      obj_per_ring = case_when(
        lab == "rf" ~ sample(c(5,10), n(), replace=TRUE), #Rodaia and Faubert (2017) tested only 5 and 10 objects per ring
        lab == "holcombe" ~ sample(c(4,8), n(), replace = TRUE) #Holcombes lab tested only 4 and 8 objects per ring
      )
    )
  
  return (sim_conditions)
}


self_test<-FALSE
if (self_test) {
  numSubjects<- 50
  trialsPerCondition<- 5
  targetNumConds<- c(2,3)
  #Array of speeds (not very realistic because mostly controlled by a staircase in actual experiment)
  speeds<-seq(.02,1.8, length.out = 12) # trials at 12 different speeds between .02 and 1.8
  
  trials <- generate_conditions_both_labs(numSubjects,trialsPerCondition,targetNumConds,speeds)
}

