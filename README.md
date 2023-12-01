# Set the path to save data
Edit setdatadir.py to appoint the directory
```
savedir = "/home/nfs/sgao/SBND_Installation/data/1129/"
```
# CE debugging mode (No interference between DAQ and CE)
Under this mode, CE is configurate by python script. 
 ## Turn Crates power on
one or multiple crates. 
## use top_on.py to turn ON FEMBs on the desired crate
```
python top_on.py
```
note: operations are only valid to the chosen crates. crates unchosen remain as is.

## use top_chk.py to configurate FEMBs in calibration/pulse mode
```
python top_chk.py
```
note: operations are only valid to the chosen crates. crates unchosen remain as is.
 
## use top_rms.py to configurate FEMBs in noise mode
```
python top_rms.py
```
note: operations are only valid to the chosen crates. crates unchosen remain as is.

## use top_off.py to turn OFF FEMBs on the desired crate
```
python top_off.py
```
note: operations are only valid to the chosen crates. crates unchosen remain as is.

## use top_ld.py to collect data without any configuration operation. 
```
python top_ln.py
```
note: operations are only valid to the chosen crates. crates unchosen remain as is.
**note: please only choose crates having performed top_chk.py or top_rms.py.** 

## suggested procedure for CE debugging mode
**It is suggested to turn ON/OFF ALL FEMBs on all 4 crates, or 2 crates the same side APA (Crate1&2, crate3&4) .** 
```
edit setsavedir.py and save.  
python top_on.py  
python top_chk.py  
python top_ld.py  
python top_ld.py  
python top_rms.py  
python top_ld.py  
python top_ld.py  
python top_off.py  
```

# Commissioning mode 
Under commissioning mode, DAQ/Slow Control handle ALL CE configuration.
We can still peek data through Slow Control (Ethernet) without changing any configuration to CE. 
To do this, DAQ/Slow Control MUST release the UDP socket of ALL WIBs so that python script can take over. 
Only top_ld.py is used in the commissioning mode. 

```
edit setsavedir.py and save.  
python top_ld.py  
python top_ld.py  
```
# SBND DATA Analysi
## data collected by top_chk.py or top_rms.py 
Use "femb_plot.py" to generate result for each FEMB. 
```
edit Line#33 and Line#34 to locate the destination raw file. 
python femb_plot.py
```
## data collected by top_ld.py or top_rms.py 
Use SBND_APA_ANA.py to generate result for the whole SBND channels. 
```
edit Line#282 to locate the destination directory. 
python SBND_APA_ANA.py
```

# SBND APA mapping generation
Use SBND_mapping.py to generate SBND_mapping.csv
```
python SBND_mapping.py
```
Note: It is not necessary to re-generate the mapping file until there is inconsistent mapping. 


