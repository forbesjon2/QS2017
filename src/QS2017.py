#volatility within a range 21
#pipeline itself
from quantopian.pipeline import Pipeline
import numpy as np
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume, SimpleMovingAverage, AnnualizedVolatility
import pandas
import datetime
import quantopian.optimize as opt
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.factors.eventvestor import BusinessDaysUntilNextEarnings
 
    
def initialize(context):
    
    #sell criteria the morning of -_-
    schedule_function(sellaII, date_rules.every_day(),
                      time_rules.market_open(minutes = 1))
    
    #cancel all open orders before buy criteria
    schedule_function(sellaIII, date_rules.every_day(),
                      time_rules.market_close(minutes = 8))
    
    #sell all (4 mins before sell all positions)
    schedule_function(selaV, date_rules.every_day(),
                      time_rules.market_close(minutes = 7))
    
    for i in range(30,380):
        schedule_function(sell_criteria, date_rules.every_day(),
                          time_rules.market_open(minutes = i))
    
    #pipeine initialization (2 mins before buy criteria)
    schedule_function(be4tradestart, date_rules.every_day(),
                      time_rules.market_close(minutes = 6))
    
    #buy criteria (3 mins before sell criteria day of)
    schedule_function(examplee, date_rules.every_day(),
                      time_rules.market_close(minutes=5))
    
    schedule_function(mmarket, date_rules.every_day(),
                      time_rules.market_close(minutes = 1))
    
    
    
    set_commission(commission.PerTrade(cost=0))
    set_commission(commission.PerShare(cost=0, min_trade_cost=0))
    set_slippage(slippage.VolumeShareSlippage(volume_limit=1, price_impact=0))
 
 
    avg_volume = AverageDollarVolume(window_length=10)
    sma_2 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length = 2)
    sma_200 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length = 200)
    avg_volumee = AverageDollarVolume(window_length = 2)
    volatilityy = AnnualizedVolatility(annualization_factor = 252)
 
    pipe_screen = ((avg_volume >= 15000000) & (sma_2 >= sma_200) & (avg_volumee >= 3000000) & (sma_2 >= 5.0) & (volatilityy <= 0.93))
    
    pipe_columns = {'avg voI': avg_volume, 'sma2': sma_2, 'sma200': sma_200, 'avg voII': avg_volumee, 'volatility': volatilityy}
    pipe=Pipeline(columns=pipe_columns, screen=pipe_screen)
    attach_pipeline(pipe, 'example')
    set_long_only()
    
    
 
def be4tradestart(context, data):
    output = pipeline_output('example')
    context.my_securities=output.sort_values('volatility', ascending=True)
 
    context.security_list = context.my_securities.index
        
    
def sellaII(context, data):
    positionss = context.portfolio.positions
    for positionz in positionss:
        boughtt = context.portfolio.positions[positionz].cost_basis
        take_profit = (boughtt*0.0052 + boughtt)
        profit_float = ('%.2f' %take_profit)
        priice = float(profit_float)
        order_target(positionz, 0, style = LimitOrder(priice))
        print("sellAII " + str(positionz) + " at " + str(priice))
        #REST?
        
            
def sellaIII(context, data):
    open_orders = get_open_orders()  
    # open_orders is a dictionary keyed by sid, with values that are lists of orders.  
    if open_orders:  
        # iterate over the dictionary  
        for security, orders in open_orders.iteritems():  
            # iterate over the orders  
            for order in orders:  
                cancel_order(order)
                #REST?
                print ("Cancelled order " + str(order))
    else:
        pass
    
def sell_criteria(context, data):
    #cancel all open orders
    open_orders = get_open_orders()
    # open_orders is a dictionary keyed by sid, with values that are lists of orders.  
    if open_orders:  
        # iterate over the dictionary  
        for security, orders in open_orders.iteritems():  
            # iterate over the orders  
            for order in orders:
                #REST?
                print ("cancelling order " + str(order))
                cancel_order(order)
    else:
        pass
    
    #now set a trailing stop loss
    exchange_time = str(get_datetime('US/Eastern'))      

    hourz = int(exchange_time[10:13])
    minutez = int(exchange_time[14:16])
    
    #change this to set the stop loss, currently at 3%
    stop_pct = 0.025
    
    minutes = minutez - 30
    hours = 60 * (hourz - 9)
    tpassed = (hours + minutes)
    
    #decay multiplier, happens every 12 minutes 
    multiplier = (tpassed // 12)
    multiplierr = (multiplier + 1)
    
    #stop loss gets 0.085% smaller every 12 minutes
    stop_percent = (stop_pct - (multiplierr* 0.00075))
    
    positionss = context.portfolio.positions
    
    for positionz in positionss:
    #price bought at, current price, historical prices
        boughht = float(context.portfolio.positions[positionz].cost_basis)
        curent_price = float(data.current(positionz, "price"))
        historicalD = data.history(positionz, "price", tpassed, '1m')
        
    #max value, calculate stop price
        gett = max(list(historicalD))
        stop_price = float(gett - (stop_percent * boughht))
        num_shares = context.portfolio.positions[positionz].amount
    
        if curent_price <= stop_price and (num_shares > 0):
            #REST?
            print ("selling psoitioz in sell criteria " + str(positionz))
            order_target_value(positionz, 0)
        else:
            pass
    
    
def mmarket(context, data):
    #cancel all open orders
    positionz = context.portfolio.positions
    ppositionz = len(positionz)
    open_orders = get_open_orders()
    oopen = len(open_orders)
    eret = (oopen + ppositionz)
    ttotal = context.portfolio.portfolio_value
    cassh = context.portfolio.cash
    if(eret == 0):
        print("stop being having autsim")
    else:
        amt_per_pos = (ttotal/eret)
    
    if open_orders:  
        # iterate over the dictionary  
        for security, orders in open_orders.iteritems():  
            # iterate over the orders  
            for order in orders:  
                cancel_order(order)
            if cassh >= amt_per_pos:
                order_target_value(security, amt_per_pos)
                #REST?
                print ("ordering " + str(security) + " at " + str(amt_per_pos))
    else:
        pass
    
    
            
    
 
def selaV(context, data):
    positionz = context.portfolio.positions
    for positioz in positionz:
        shrs = context.portfolio.positions[positioz].amount
        if shrs >= 0:
            #REST?
            print ("selAV " + str(positioz))
            order(positioz, 0)
        else:
            pass
 
            
            
def examplee(context, data):
    #safeguard against holding past the selloff time
    cassh = context.portfolio.cash
    possitions = context.portfolio.portfolio_value
    if cassh != possitions:
        positionz = context.portfolio.positions
        for positioz in positionz:
            #REST?
            print ("selling all of " + str(positioz))
            order_target(positioz, 0)
    
    
    tetris = list(context.security_list)
    tetris.reverse()
    
    erange = len(context.security_list)
    rangee = range(1, erange)
    wtwer = 0
    ee = 0
    ptestt = []
    
    if ee == 0:
        for numm in rangee:
            rentx = (numm -1)
            if (wtwer < 5):
                H = data.history(tetris[rentx], 'high', 3785, '1m')
                L = data.history(tetris[rentx], 'low', 3785, '1m')
                C = data.history(tetris[rentx], 'price', 6, '1m')    
                CC = data.history(tetris[rentx], 'price', 1, '1m')
            
            
            #define lookback period for High & find max
            #Use only for first lookback period, gets most recent value & includes that into 1st iteration
                hii = H[-2940 :: 1]
                hii2 = H[-3149 : -209 : 1]
                hii3 = H[-3359 : -419 : 1]
                hii4 = H[-3569 : -629 : 1]
                hii5 = H[-3779 : -839 : 1]
            
            
                hi01 = max(hii)
                hi02 = max(hii2)
                hi03 = max(hii3)
                hi04 = max(hii4)
                hi05 = max(hii5)
            

        #define lookback period for Low & find min
        #Use only for the first lookback period, gets most recent value & includes that into 1st iteration

                loo = L[-2940::1]
                loo2 = L[-3149 : -209 : 1]
                loo3 = L[-3359 : -419 : 1]
                loo4 = L[-3569 : -629 : 1]
                loo5 = L[-3779 : -839 : 1]
                     
            
                low01 = min(loo)
                low02 = min(loo2)
                low03 = min(loo3)
                low04 = min(loo4)
                low05 = min(loo5)
     
        #current close
                ccc00 = CC
                ccc01 = C[-2]
                ccc02 = C[-3]
                ccc03 = C[-4]
                ccc04 = C[-5]
            
            
            
#-----------------------Percent D (%D)---------------------------------#
                
                A00 = (ccc00 - low01)
                A01 = (ccc01 - low02)
                A02 = (ccc02 - low03)
                A03 = (ccc03 - low04)
                A04 = (ccc04 - low05)
            
            
                B00 = (hi01 - low01)
                B01 = (hi02 - low02)
                B02 = (hi03 - low03)
                B03 = (hi04 - low04)
                B04 = (hi05 - low05)
            
            
                PercentD_num = (A00 + A01 + A02)
                PercentD_den = (B00 + B01 + B02)
            
                PercentD_num01 = (A01 + A02 + A03)
                PercentD_den01 = (B01 + B02 + B03)
            
                PercentD_num02 = (A02 + A03 + A04)
                PercentD_den02 = (B02 + B03 + B04)
                
            
                PercentD = (((PercentD_num / PercentD_den) * 100))
                PercentD01 = (((PercentD_num01 / PercentD_den01) * 100))
                PercentD02 = (((PercentD_num02 / PercentD_den02) * 100))
            
            
            #Signal line
                Sig = ((PercentD + PercentD01 + PercentD02) / 3)
            
                PercentDd = float(PercentD)
                Sigg = float(Sig)            

           

                if PercentDd <= 21 and Sigg <= 21:
                    wtwer += 1
                    ptestt.append(tetris[rentx])

                else:
                    pass        
    
            else:
                pass
            
    p_length = (len(ptestt))
    
    if p_length <= 4 and p_length < 2:
        pcash = possitions/p_length
        for poss in ptestt:
             curentprice = data.history(poss, fields = "price", bar_count = 1,
                                        frequency = "1m")
             crrntprii = np.mean(curentprice)
             pri_float = ('%.2f' %crrntprii)
             erty = float(pri_float)
                
             amt_PerTrde = (pcash/erty)
             buyy = int(amt_PerTrde)
             byy = (buyy*erty)
             byyy = int(byy)
             if context.portfolio.cash >= byyy:
                 #REST?
                 print ("ordering " + str(poss) + " and " + str(byyy) + " idk what this is " + str(erty))
                 order_target_value(poss, byyy, style=LimitOrder(erty))
        
    elif p_length > 4:
        plength = ptestt[:4]
        pcassh = possitions/4
        for pos in plength:
             curentprice = data.history(pos, fields = "price", bar_count = 1,
                                        frequency = "1m")
             crrntprii = np.mean(curentprice)
             pri_float = ('%.2f' %crrntprii)
             erty = float(pri_float)
                
             amt_PerTrde = (pcassh/erty)
             buyy = int(amt_PerTrde)
             byy = (buyy*erty)
             byyy = int(byy)
             if context.portfolio.cash >= byyy:
                 #REST?
                 print ("ordering " + str(pos) + " and " + str(byyy) + " idk what this is " + str(erty))
                 order_target_value(pos, byyy, style=LimitOrder(erty))

    else:
        pass