library(tidyverse)
library(brms)

# Creating Simulated Data
# In order to build and test our model in brms, we must first create a simulated data set that is similar to our actual experiment data. This allows us to confirm the brms model is working and successfully recovers the parameters we set before applying it to our real experimental data that has unknown parameter values. In the actual data, there will be many group-wise differences in location and scale parameters. The following simulated data only has explicit differences between the $\eta$ (location) of the two age groups (older vs younger).

generate_conditions<- function(laboratories,numSubjects,trialsPerCondition,targetNumConds,speedsPerCond) {
  #e.g.:
  #numSubjects<- 50
  #trialsPerCondition<- 5
  #targetNumConds<- c(2,3)
  #Array of speeds (not very realistic because mostly controlled by a staircase in actual experiment)
  #speeds<-seq(.02,1.8, length.out = 12) # trials at 12 different speeds between .02 and 1.8
  
  #Generate data frame for simulated data
  sim_conditions <- tidyr::expand_grid(
    lab= laboratories,
    gender = c("F","M"),
    age_group = c("older","younger"),
    subjWithinGroup = seq(1, numSubjects), #subjects
    num_targets = targetNumConds, #number of targets particpant tracks
    obj_per_ring = c("fewer","more"),
    trialThisCond = seq(1,trialsPerCondition), #replicates of each trial combination
    speed = speeds
  )
  
  # Set number of objects per ring based on lab
  sim_conditions <- sim_conditions %>%
    mutate(
      obj_per_ring = if_else(lab=="Holcombe",if_else(obj_per_ring=="fewer",4,8),
                                             if_else(obj_per_ring=="fewer",5,10)) #Roudaia lab
    )
  
  return (sim_conditions)
}

self_test<-FALSE
if (self_test) {
  laboratories<- c("Roudaia", "Holcombe")
  subjPerGroup<- 50
  trialsPerCond<- 8
  targetNumConds<- c(2,3)
  #Array of speeds (not very realistic because mostly controlled by a staircase in actual experiment)
  speeds<-seq(.02,1.7, length.out = 12) # trials at 12 different speeds between .02 and 1.8
  
  trials <- generate_conditions(laboratories,subjPerGroup,
                                trialsPerCond,targetNumConds,speeds)
  
  #Print number of unique values of each column
  numValsPerFactor<- trials |> summarise(across(everything(), ~ n_distinct(.))) |>
    pivot_longer(everything())
  print( numValsPerFactor )
  
  ##sanity-check that unbalanced if filter weirdly:
  trialsDefinitelyUnbalanced<- trials |> filter( ! ( subjWithinGroup != "1" & num_targets != "2" & trialThisCond==1) ) 
  
  #If below has more than one row, it means there are multiple different counts for the combinations—
  #so the combinations are not balanced.
  #If it has exactly one row, then all combinations occur equally often (i.e., are balanced).
  unbalanced<- trials %>% 
    group_by(lab, gender, age_group, subjWithinGroup, num_targets, obj_per_ring) %>%
    summarise(numGroups = n(), .groups = "drop") %>%
    count(numGroups)
  unbalanced <- nrow(unbalanced) > 1
  if (unbalanced) {
    print('unbalanced lab, gender, age_group, subjWithinGroup, num_targets, obj_per_ring = ',
          as.logical(unbalanced))
  }
  
  #Confirm that each condition has trials numbered 1 to trialsPerCond
  groupedByCond<- trials |> group_by(lab,gender,age_group,subjWithinGroup,
                                     num_targets,obj_per_ring,speed) 
  groupedByCond<- groupedByCond |> summarise(n=n(),.groups="drop") |> 
    select(n)  |> distinct() #Should be one row only
  if ((nrow(groupedByCond) != 1)  |  (groupedByCond$n[1] != trialsPerCond)) {
    print("The conditions somehow don't have trialsPerCond trials")
  }
  
  #Create "trial" that numbers trials by subject rather than by subj*cond
  #So far I don't have a trial number for the subject, I only have a trialThisCond column
  #Calculate a trial number numbering the entirety of the trials the subject is given
  #Assume the within-participant factors are obj_per_ring,num_targets, and speed
  trials <- trials |> group_by(lab,trialThisCond,age_group,gender,subjWithinGroup) |> 
    mutate(trial = row_number())
  cat('Trials per participant should be ',2*length(targetNumConds)*length(speeds),
      'and it is:',max(trials$trial))
  
  #Check that subject behaves like I expect.
  data_one_subject_group <- trials |> 
    filter(age_group=="younger",gender=="M",lab=="Holcombe")
  trialsPerSubject<- length(targetNumConds) * 2 * length(speeds) * trialsPerCond
  subjectsTrials<- table(data_one_subject_group$subjWithinGroup)
  distinctTrialsPerSubject <- unique(subjectsTrials)
  if (length(distinctTrialsPerSubject) > 1) {
    print('Somehow different subjects have different numbers of trials.')
  }
  cat('Trials per participant should be ',trialsPerSubject,
      'and it is:',as.numeric(subjectsTrials[1]))
  
  numSsPerGroup <- length( table(data_one_subject_group$subjWithinGroup) )
  if (numSsPerGroup != subjPerGroup) {
    print("Not sure num subjects worked right.")
  }
  
  data_one_subject_cond <- trials |> 
    filter(num_targets==2,age_group=="younger",gender=="M",lab=="Holcombe")
  
  numSsPerGroup <- length( table(data_one_subject_group$subjWithinGroup) )
  if (numSsPerGroup != subjPerGroup) {
    print("Not sure num subjects worked right.")
  }
  
}

