 #突破追
        if (self.H2_breakout_flag and cur_bar-self.H2_breakout_index>5):
           
            if (avg_price > self.HH2):
                pass
            elif (avg_price < self.HH1):
                pass
            elif (avg_price < self.LL1):
                self.H2_breakout_flag = False

            if (cur_bar-self.H2_breakout_index > self.FLOW_GAP_BAR):#时间 default:5
                pass
            elif(avg_price > self.HH2 +10):
                tmp_position = 1