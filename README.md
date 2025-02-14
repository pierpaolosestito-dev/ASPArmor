# **ASP Armor Execution Modes: Security & Isolation**

This repository contains four scripts demonstrating different execution modes for running **Clingo** in a web app environment. The scripts explore various levels of security and isolation to mitigate **remote code execution (RCE) vulnerabilities** while balancing usability for SSH users.

## **Scripts Overview**

### **1️⃣ Unconfined Execution: `run-unconfined.sh`**
🚨 **Vulnerable to RCE** | ⚠ **No Security Restrictions**

This script sets up a web app that runs **Clingo** without any confinement, making it vulnerable to **remote code execution (RCE)** attacks. If exploited, an attacker can take full control of the system.

🔹 **Use Case:** Demonstrates the risk of running Clingo without any protection.

🔹 **Impact:**
- The web app **can be compromised** and **take over the system**.
- SSH users **retain full access** to Clingo without restrictions.

📌 **Run:**
```bash
./run-unconfined.sh
```

---

### **2️⃣ Confined Execution via AppArmor: `run-confined-via-apparmor.sh`**
🛡 **Protected Against RCE** | 🔒 **Restricts All Users**

This script enforces security using **AppArmor**, ensuring that Clingo within the web app **cannot be exploited** for remote code execution.

🔹 **Use Case:** Adds security but applies restrictions to **all users**, including SSH users.

🔹 **Impact:**
- The web app **is safe from RCE vulnerabilities** ✅
- **SSH users are subject to the same restrictions**, making normal usage difficult ❌

📌 **Run:**
```bash
./run-confined-via-apparmor.sh
```

---

### **3️⃣ Confined Execution via UserArmor: `run-confined-via-userarmor.sh`**
🛡 **Protected Against RCE** | ✅ **SSH Users Unrestricted**

This script uses **UserArmor**, an extension of AppArmor, to enforce security only for the web app **while allowing SSH users to run Clingo normally**.

🔹 **Use Case:** Provides a balance between **security and usability**.

🔹 **Impact:**
- The web app **is protected from RCE** ✅
- **SSH users remain unrestricted** ✅

📌 **Run:**
```bash
./run-confined-via-userarmor.sh
```

---

### **4️⃣ Sandboxed Execution via Bubblewrap: `run-sand-boxed-via-bwrap.sh`**
🛡 **Protected Against RCE** | 🛑 **Each Execution Isolated**

This script runs Clingo in a **Bubblewrap sandbox**, ensuring the web app runs in an isolated environment.

🔹 **Use Case:** Provides strong isolation at the cost of spawning a **new sandbox instance per execution**.

🔹 **Impact:**
- The web app **is protected from RCE** ✅
- **Each execution requires a separate isolated environment**, impacting performance ⚠

📌 **Run:**
```bash
./run-sand-boxed-via-bwrap.sh
```

---

## **Summary: Choosing the Right Execution Mode**
| Execution Mode | RCE Protection | SSH Users Unrestricted? | Fast (no Sandbox)? |
|---------------|---------------|------------------|----------------|
| **Unconfined (`run-unconfined.sh`)** | ❌ No | ✅ Yes | ✅ Yes |
| **AppArmor (`run-confined-via-apparmor.sh`)** | ✅ Yes | ❌ No | ✅ Yes |
| **UserArmor (`run-confined-via-userarmor.sh`)** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Bubblewrap (`run-sand-boxed-via-bwrap.sh`)** | ✅ Yes | ✅ Yes | ❌ No |

---

## **Usage Instructions**

Ensure you have the necessary dependencies installed before running the scripts.

### **Install AppArmor & Bubblewrap (If Not Installed)**
```bash
sudo apt install apparmor bubblewrap
```

### **Run a Specific Script**
```bash
./run-confined-via-userarmor.sh
```

For debugging, check logs:
```bash
dmesg | grep DENIED
```

---

## **📌 Conclusion**
This project demonstrates different security mechanisms to **protect Clingo from RCE vulnerabilities** while balancing usability for SSH users. Choose the appropriate script based on your security and usability requirements.

🚀 **Contributors & Feedback:** Feel free to submit issues or suggestions!


