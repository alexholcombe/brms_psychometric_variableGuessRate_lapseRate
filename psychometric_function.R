library(tidyverse)

#Add column for the probability of each trial being correct based on our psychometric function
#then add column to generate if the subject got the trial correct

#phi refers to the core curve of the psychometric function before incorporating lapse rates, chance, etc.
#It goes from negative inf to positive infinity, decreasing from 1 to 0
#eta is the location parameter or 50% point of speed
#sigma is the scale parameter
phi<- function(speed,eta,sigma) {
  #pnorm is one option, it is the cdf of the normal distribution
  ans = pnorm(-speed, -eta, sigma)
  return(ans)
}

#If one wrote the expression for the psychometric function from first principles,
#c: chance rate
#l: lapse rate
#phi: Assuming no lapse, probability get it right, as a function of speed (s)
#lc + (1-l)( phi + (1-phi)c )
#Two phi terms in this high-threshold model, one for when track correctly: phi
#and one to calculate the chance of getting it right when you don't track correctly: (1-phi)*c 

#Having two invocations of phi probably wouldn't work well with Bayes and other function fitting
#The algebra leading to Equation A.6 in Schutt et al. 2016 shows 
#that we can avoid having two invocations of phi by reparameterizing this equation,
#keeping chance rate (which they denote with gamma) but introducing lambda = l(1-c).
#That yields: c + (1 - c - lambda)p , but using that would prevent putting a prior on lapse
#So we don't adopt that aspect below.

psychometric_function<- function(c,l, speed,eta,sigma) {
  #c is chance_rate
  #l is lapse_rate
  
  #range - amplitude of percent correct as constrained by lapse rate and chance rate
  #min = c
  #max = l*c + (1-l)*1
  #    = l*c + 1 + -l
  #range = max        - min
  #range = l*c + 1 -l - c
  #      = 1-c + l*c - l     #simplifying
  #      = 1-c + l*(c-1)
  #      = 1-c - l(-c+1)
  #      = 1-c - l(1-c)
  #      = 
  range = 1-c - l*(1-c)
  
  ans = c + range * phi(speed,eta,sigma)
  
  return (ans)
}

make_example_plot <- TRUE
if (make_example_plot) {
  
  example <- dplyr::tibble(
    speed = seq(0,2.5, length.out = 500),
    c = 0.25,
    l = 0.1, 
    eta = 0.9,
    sigma = 0.2,
    upper_bound = l*c + 1-l,
    p_correct = psychometric_function(c,l,speed,eta,sigma)
  )

  ggplot(example) + 
    geom_hline(aes(yintercept = upper_bound, colour = "Upper Bound"), linetype = "dashed") +
    geom_hline(aes(yintercept = 0.25 , colour = "Lower Bound"), linetype = "dashed") +
    geom_vline(aes(xintercept = 0.9, colour = "eta")) +
    geom_line(aes(x = speed, y = p_correct,
                  colour = "Probability Correct")) +
    theme_light() +
    lims(x = c(0,2.5), y = c(0,1)) +
    scale_colour_manual(values = c("Upper Bound" = "blue", "Lower Bound" = "red", "eta" = "yellow", "Probability Correct" = "black")) +
    labs(colour = "Legend",
         x = "Speed (revolutions per second)",
         y = "P(Correct)",
         title = "Example of Psychometric Function")
}