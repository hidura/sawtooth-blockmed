Before add the evaluation you'll have to add a consent, to do that you can go to the index page on the webmod and add the
IDCard that is the main reference on to track the people on the system.
Once you've add the consent then you can make a POST request, to the `http://localhost:8041/api/evaluations`
The next are the parameters that are required some are necessary(bold ones), other are optionals.

## These are the fields used by the `https://gnuhealth.org/` system to store the evaluations, so anybody with 
GNU/Health can use it

##### idcard_patient -> The id card of the patient which evaluation record is going to receive the information.
##### idcard_doctor  -> The id card of the doctor that will send the evaluation.
##### idcard_type    -> 1 for IDCARD; 2 RNC; 3; PASSPORT
abdominal_circ 
abstraction 
bpm 
diagnosis
info_diagnosis
chief_complaint
cholesterol_total
dehydration
derived_from
derived_to
diagnosis
diastolic
directions
discharge_reason
evaluation_endtime
evaluation_start
evaluation_summary
evaluation_type
fat_percentage
glycemia
hbac 
hdl 
head_circumference 
healthprof 
height 
hip 
info_diagnosis 
information_source 
institution
judgment 
knowledge_current_events 
ldl 
loc 
loc_eyes 
loc_motor 
loc_verbal 
malnutrition 
memory 
mood 
next_evaluation 
notes 
notes_complaint 
object_recognition  
orientation  
osat  
patient  
praxis  
present_illness  
related_condition
reliable_info  
respiratory_rate  
signed_by  
specialty 
state 
systolic 
tag 
temperature 
tremor 
urgency
user_id  
violent  
visit_type  
vocabulary  
weight  
whr  
ggt  
homocysteine  
left_arm  
left_thigh
level_fat_visc  
metabolic_rate  
mg  
muscle_mass  
pos_glocose  
pos_insulin  
pre_glocose  
pre_insulin  
reactive_protein_c  
right_arm

right_thigh 

tsh 

uric_acid

vitaminD 

calculation_ability 
