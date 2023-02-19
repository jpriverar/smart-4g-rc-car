import time

def steering_test(uart):
    print("Starting unit test on steering module")
    
    def get_current():
        uart.send_msg("SG")
        time.sleep(1)
        return uart.msg_queue.popleft()
    
    passed = 0
    total = 0
    
    # Current steer angle
    msg = get_current()
    print("Recieved message: " + msg)
    
    # Setting to new angle
    total += 1
    target = "120"
    uart.send_msg("SS" + target)
    time.sleep(0.1)
    msg = get_current()
    passed += msg == target
    
    # Increasing the current angle
    total += 1
    msg = get_current()
    increase = "10"
    target = str(int(msg) + int(increase))
    uart.send_msg("SI" + target)
    msg = get_current()
    passed += msg == target
    
    print(f"{passed}/{total} Test passed")