# ecobici_analysis
Data analysis around the open data from the Ecobici bike rental service in Mexico City

This project is structured around the following ideas:

a. Present a helpful, insightful and fun visualization service of the bike rental statistics.

b. Develop data exploration abilities.

c. Predict usage.

d. Read the geographic data science literature on related analysis and build on top of that knowledge.

# TODO

The following is a list of things that I better write before I forget:

1. Visualize use of bikes by day of the week. DONE.

2. Find cumulative use for each station. DONE

3. Find a better geographical visualization library, in particular, one that allows me to visualize several routes and do animations of travels. osmnx has been super useful in allowing me to find shortest routes between stations, since I will be assuming that these are the routes taken by riders. But I haven't found a way to show several paths simultaneously. PLOTLY DASH CHOSEN. LEAFLET CHOSEN.

4. Predict the mobility in CDMX! Maybe use a recurrent nn.

5. Find clusters of stations. I remember having to go somewhere else nearby to take or lock a bike.

6. Find the time evolution of usage (total, by sex, etc). This implies downloading more files and devising a way of accessing them in an efficient way, something that, at the moment, have no idea how to do.