import time
from scapy.all import sniff
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)

# Global variables
total_bytes = 0
start_time = time.time()

#Count total bytes
def packet_callback(packet):
    global total_bytes
    total_bytes += len(packet)

#calculate bandwidth and generate chart
def bandwidth_monitor(interface, duration, interval):
    global total_bytes, start_time

    print(f"Monitoring bandwidth on interface {interface} for {duration} seconds...")
    
    end_time = start_time + duration
    times = []
    band = []

    #calculate total bytes transfered per interval
    while time.time() < end_time:
        
        sniff(iface=interface, prn=packet_callback, timeout=interval) #start capture
        interval_start = time.time()
        times.append(interval_start) #append interval start time to "times" list
        interval_end = interval_start + interval
        elapsed_time = interval_end - interval_start
        bandwidth = total_bytes / (1024 * elapsed_time) #calculate bandwidth per interval
        band.append(bandwidth) #append bandwidth to "band" list
        
        print(f"Average bandwidth: {bandwidth:.2f} KB/s")

        time.sleep(interval)

    #Chart
    plt.plot(times, band)
    plt.savefig("static/images/bandwidth_chart.png")
    plt.close()

#Text box that accepts an integer input for "duration" var
@app.route('/', methods=['GET','POST'])

def duration_input():
    if request.method == "POST":
        try:
            duration = int(request.form['duration'])
            render_chart = bandwidth_monitor(interface, duration, interval)
            return render_template("duration_input.html", render_chart=render_chart)
        except ValueError:
            return "Invalid Input"
    return render_template("duration_input.html")


if __name__ == "__main__":
    interface = "Wi-Fi"   
    interval = 1

    app.run(debug=True)
