ifeq ($(CXX), clang++)
	COVFLAGS := --coverage
	GCOV     := gcov-4.6
else
	COVFLAGS := -fprofile-arcs -ftest-coverage
	GCOV     := gcov-4.8
endif

CXXFLAGS := -pedantic -std=c++11 -O3 -Wall
CFLAGS   := -std=c99 -O3 -Wall
ifndef VARS
	LDFLAGS  := -lwiringPi
endif
VALGRIND := valgrind

all : read_dht11

read_dht11 :
	$(CC) $(CFLAGS) $(LDFLAGS) read_dht11.c -o read_dht11

test: all
	sudo ./read_dht11

clean :
	rm -f read_dht11

-include *.d
