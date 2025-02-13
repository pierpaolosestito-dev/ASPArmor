# Compiler
CC = gcc

# Compiler flags
CFLAGS = -Wall -Wextra -Wpedantic -O2 -g

# Target executable
TARGET = ua-generate

# Source files
SRC = ua-generate.c

# Object files (automatically generated from SRC)
OBJ = $(SRC:.c=.o)

# Default target
all: $(TARGET)

# Build executable
$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

# Compile source files into object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(OBJ) $(TARGET)

# Phony targets (to prevent filename conflicts)
.PHONY: all clean

install: $(TARGET)
	sudo cp $(TARGET) /usr/bin/

uninstall:
	sudo rm -f /usr/bin/$(TARGET)
    
