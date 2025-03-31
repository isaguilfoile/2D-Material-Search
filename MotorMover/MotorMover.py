from ConexCC import ConexCC

if __name__ == "__main__":
    ConexCC.dump_possible_states()
    motor_x = ConexCC(com_port='com5', velocity=0.5, max_velocity=0.4, dev=1) # TODO: We might have to analyze ports, why is max velocity less than velocity?
    ready = motor_x.wait_for_ready(timeout=60)
    if ready:
        motor_x.move_absolute(motor_x.max_limit / 2)
        ready = motor_x.wait_for_ready(timeout=60)
        if ready:
            motor_x.move_relative(-3)
            ready = motor_x.wait_for_ready(timeout=60)
            if ready:
                print('ok!')
            else:
                print('not ok 2!')
        else:
            print('not ok 1!')
        motor_x.close()
    else:
        print('something went wrong')