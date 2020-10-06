#!/usr/bin/env python
# coding: utf-8

# In[27]:


import sqlite3 as sql
import os


# In[40]:


##gets ROC & Average Fuel consumption, based on aircraft weight, outside air temp & altitude
def getClimbingFlightPointData(cursor, weight, temp, altitude):
    sqlite_select_query = """SELECT * from data where weight=? AND temp=? AND altitude=?"""
    cursor.execute(sqlite_select_query,(weight,temp,altitude))
    return cursor.fetchall()


# In[41]:


##gets ROC & Average Fuel consumption, based on aircraft weight, outside air temp & altitude
def getLeveledFlightPointData(cursor, weight, temp, altitude):
    sqlite_select_query = """SELECT * from data where weight=? AND temp=? AND altitude=?"""
    cursor.execute(sqlite_select_query,(weight,temp,altitude))
    return cursor.fetchall()


# In[42]:


##gets ROC & Average Fuel consumption, based on aircraft weight, outside air temp & altitude
def getDescendingFlightPointData(cursor, weight, temp, altitude):
    sqlite_select_query = """SELECT * from data where weight=? AND temp=? AND altitude=?"""
    cursor.execute(sqlite_select_query,(weight,temp,altitude))
    return cursor.fetchall()


# In[43]:


##gets averaged data, during climb, weight, fuel, starting parameters
def getClimbingFlightData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    cwd = os.getcwd()
    try:
        conn=sql.connect(cwd+"\\database\\"+aircraftType+".climbing.sqlite")
    except Error as e:
        print("Could not connect to database...")
    
    cursor = conn.cursor()
    totalWeight=weight+fuel
    startRecords = getClimbingFlightPointData(cursor,totalWeight,startTemp,startAlt)
    endRecords= getClimbingFlightPointData(cursor,totalWeight,endTemp,endAlt)
    cursor.close()
    avgROC=(startRecords[0][3]+endRecords[0][3])/2
    avgFC=(startRecords[0][4]+endRecords[0][4])/2
    return [avgROC,avgFC]


# In[44]:


##gets averaged data, during leveled flight, weight, fuel, starting parameters
def getLeveledFlightData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    cwd = os.getcwd()
    try:
        conn=sql.connect(cwd+"\\database\\"+aircraftType+".leveled.sqlite")
    except Error as e:
        print("Could not connect to database...")
    
    cursor = conn.cursor()
    totalWeight=weight+fuel
    startRecords = getLeveledFlightPointData(cursor,totalWeight,startTemp,startAlt)
    endRecords= getLeveledFlightPointData(cursor,totalWeight,endTemp,endAlt)
    cursor.close()
    avgROC=(startRecords[0][3]+endRecords[0][3])/2
    avgFC=(startRecords[0][4]+endRecords[0][4])/2
    return [avgROC,avgFC]


# In[48]:


##gets averaged data, during descend, weight, fuel, starting parameters
def getDescendingFlightData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    cwd = os.getcwd()
    try:
        conn=sql.connect(cwd+"\\database\\"+aircraftType+".descending.sqlite")
    except Error as e:
        print("Could not connect to database...")
    
    cursor = conn.cursor()
    totalWeight=weight+fuel
    startRecords = getDescendingFlightPointData(cursor,totalWeight,startTemp,startAlt)
    endRecords= getDescendingFlightPointData(cursor,totalWeight,endTemp,endAlt)
    cursor.close()
    avgROC=(startRecords[0][3]+endRecords[0][3])/2
    avgFC=(startRecords[0][4]+endRecords[0][4])/2
    return [avgROC,avgFC]


# In[49]:


def getFlightLegData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    avgROC=1
    avgFC=0
    for pattern in flightPattern:
        if(pattern==1):
            avgROC, avgFC = getClimbingFlightData(aircraftType, pattern, weight, fuel, startTemp, endTemp,startAlt, endAlt)
        if(pattern==0):
            avgROC, avgFC = getLeveledFlightData(aircraftType, pattern, weight, fuel, startTemp, endTemp,startAlt, endAlt)
        if(pattern==-1):
            avgROC, avgFC = getDescendingFlightData(aircraftType, pattern, weight, fuel, startTemp, endTemp,startAlt, endAlt)
    return [avgROC,avgFC]


# In[50]:


avgRoc, avgFC = getFlightLegData("Airbus",[0,1,-1],14,14,40,40,13,13)
print(avgRoc)
print(avgFC)


# In[ ]:




