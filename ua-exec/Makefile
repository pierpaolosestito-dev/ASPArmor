# Compiler
CC = gcc

# Compiler flags
CFLAGS = -Wall -Wextra -Wpedantic -O2 -g

# Target executable
TARGET = ua-exec

# Source files
SRC = ua-exec.c

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
	sudo groupadd userarmor || echo "group userarmor exists!"
	sudo adduser ${USER} userarmor || echo "user already in userarmor!"
	sudo cp $(TARGET) /usr/bin/
	sudo chown root:userarmor /usr/bin/$(TARGET)
	sudo chmod +s /usr/bin/$(TARGET)

uninstall:
	sudo groupdel userarmor
	sudo rm -f /usr/bin/$(TARGET)
    
