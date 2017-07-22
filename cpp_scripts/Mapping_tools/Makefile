UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	BOOST=/usr/include
endif
ifeq ($(UNAME_S),Darwin)
	BOOST=/opt/local/include
endif
# Using gcc for now
CC=g++
# Flags for the compiles
CFLAGS=-c -Wall -O3 -g
# Samtools path
SAMTOOLS=../SamTools/
INCLUDE=include/

all: mergeMappings join findIndexes findIndexWpairEnd 

mergeMappings: mergeMappings.o
	$(CC) mergeMappings.o -o mergeMappings -L$(SAMTOOLS) -lbam -lz -lpthread

join:
	$(CC) join.cpp -fopenmp -O3 -o join

findIndexes: findIndexes.o
	$(CC) findIndexes.o -o findIndexes -L${BOOST} -lpthread -lz 

findIndexWpairEnd: findIndexWpairEnd.o
	$(CC) findIndexWpairEnd.o -o findIndexWpairEnd -L${BOOST} -lpthread -lz 

findIndexes.o: findIndexes.cpp
	$(CC) -I$(INCLUDE) -I${BOOST}  $(CFLAGS) findIndexes.cpp

findIndexWpairEnd.o: findIndexWpairEnd.cpp
	$(CC) -I$(INCLUDE) -I${BOOST} $(CFLAGS) findIndexWpairEnd.cpp
 	
mergeMappings.o: mergeMappings.cpp
	$(CC) -I$(SAMTOOLS) $(CFLAGS) mergeMappings.cpp

install:
	mkdir -p ~/bin
	cp mergeMappings ~/bin/
	cp join ~/bin/
	cp findIndexes ~/bin/
	cp findIndexWpairEnd ~/bin/
clean:
	rm -rf *o mergeMappings
	rm -rf *o join
	rm -rf *o findIndexes
	rm -rf *o findIndexeWpairEnd
