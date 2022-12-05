const clockContainer = document.querySelector("#clock")
const dateContainer = document.querySelector("#date")
const updateClock = () => {
    clockContainer.innerHTML = new Date().toLocaleTimeString()
    dateContainer.innerHTML = new Date().toLocaleDateString()
}
updateClock()

const cpuLoad = document.querySelector("#cpuLoad")
const ramLoad = document.querySelector("#ramLoad")
const updateLoad = () => {
    fetch("/api/system").then(e=>e.json()).then(data=>{
        cpuLoad.innerHTML = `${data.cpu.toFixed(1)}%`
        ramLoad.innerHTML = `${data.ram.toFixed(1)}%`
    })
}
updateLoad()

setInterval(()=>{
    updateClock()
    updateLoad()
},1000)


document.querySelector("body").classList.add(window.innerWidth > window.innerHeight ? "normal" : "phone")
const x = document.getElementById("stream");

const webSocket = new WebSocket("ws://" + window.location.host.split(":")[0] + ":8081");
webSocket.onopen = (event) => {
    // webSocket.send("Here's some text that the server is urgently awaiting!");
};
webSocket.onmessage = (event) => {
    let img = event.data.substr(11)
    img = img.substr(0,img.length-1)
    console.log("new img")
    const image = `data:image/jpeg;base64,${img}`
    x.src = image;
}

const showLines = false

const traces = {
    blue: {
        x: [],
        y: [],
        mode: showLines?'lines+markers':'markers',
        type: 'scatter',
        marker: {
            color: 'rgb(0,0,255)',
        },
        line: {
            color: 'rgba(0,0,255,.2)',
        }
    },
    red: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(255,0,0)',
        },
        line: {
            color: 'rgba(255,0,0,.2)',
        }
    },
    yellow: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(255,255,0)',
        },
        line: {
            color: 'rgba(255,255,0,.2)',
        }
    },
    green: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(0,255,0)',
        },
        line: {
            color: 'rgba(0,255,0,.2)',
        }
    },
    pink: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(255,0,255)',
        },
        line: {
            color: 'rgba(255,0,255,.2)',
        }
    },
    black: {
        x: [],
        y: [],
        type: 'scatter',
        mode: 'markers',
        marker: {
            color: 'rgb(0,0,0)',
            size: [10,5],
        }
    },
    selected: {
        x: [],
        y: [],
        // yaxis: 'y2',
        mode: 'markers',
        type: 'scatter',
        marker: {
            color: 'rgb(0,0,0)',
            size: [10],
        }
    },
}

let rawTraces = null

let range = [0,0]

const plot = () => {
    // console.log(traces)
    const x = [
        ...traces.blue.x,
        ...traces.blue.y,
        ...traces.red.x,
        ...traces.red.y,
        ...traces.yellow.x,
        ...traces.yellow.y,
        ...traces.green.x,
        ...traces.green.y,
        ...traces.pink.x,
        ...traces.pink.y,
        ...traces.black.x,
        ...traces.black.y,
        ...traces.selected.x,
        ...traces.selected.y,
    ].sort((a,b)=>a-b)
    const tempRange = [x[0]-10, x[x.length-1]+10]
    if(tempRange[0]<range[0]) range[0] = tempRange[0]
    if(tempRange[1]>range[1]) range[1] = tempRange[1]
    // console.log(range)
    // Plotly.newPlot('myDiv', Object.values(traces), {
        
    const axis = {
        autorange: false,
        zerolinewidth: 0,
        zeroline: false,
        range,
    }
    Plotly.newPlot('myDiv', Object.values(traces), {
        width: 500,
        height: 500,
        autoscale: false,
        showlegend: false,
        yaxis: axis,
        xaxis: axis
    });
}
const img = new Image()

img.onload = function() {
    x.src = img.src;
};

// setInterval(()=>{
//     // img.src = `/image?t=${new Date().getTime()}`
//     x.src = `/image?t=${new Date().getTime()}`
// },1000)
if(false){
    setInterval(()=>{
        fetch("/positions")
            .then((response) => response.json())
            .then(data=>{
                rawTraces = data

                const build = (color,arr) => {
                    if(!(color in data )) return arr
                    const x = Object.values(data[color].items).map(e=>e.x)
                    const z = Object.values(data[color].items).map(e=>e.z)
                    traces[color].x = x;
                    traces[color].y = z;

                    return [[x,...arr[0]],[z,...arr[1]]]
                }

                let val = [[],[]]
                for(let k in traces){
                    val = build(k,val)
                }
                const allx = val[0].sort()
                const allz = val[1].sort()

                const distance = 10
                const point2 = []
                const pos = data.self.items["0"];
                // console.log(t,pos.euler)
                const a = distance * Math.sin(pos.euler.y)
                const b = distance * Math.cos(pos.euler.y)
                traces.black.x = [pos.translation.x,pos.translation.x+a]
                traces.black.y = [pos.translation.z,pos.translation.z+b]

                plot()

                const html = ["<h2>Known Cones</h2>"]                    
                for(let k in data){
                    if(k==="self") continue;
                    for(let n in data[k].items){
                        html.push(`<a data-delete="" href="/delete/${k}:${n}">${k.padStart(6," ")} ${Math.round(data[k].items[n].x)} ${Math.round(data[k].items[n].z)}</a>`)
                    }
                }
                html.push(`<a data-delete="" href="/reset_cones">Delete all</a>`)

                document.getElementById("deletes").innerHTML = html.join("")
                const d = document.querySelectorAll("[data-delete]");
                for(let i=0;i<d.length;i++){
                    d[i].addEventListener("click",e=>{
                        e.preventDefault();
                        fetch(e.target.href)
                    })
                    d[i].addEventListener("mouseenter",e=>{
                        e.preventDefault();
                        const href = e.target.href.split("/")
                        const uri = href[href.length - 1].split(":")
                        const item = rawTraces[uri[0]].items[uri[1]];
                        traces.selected.x = [item.x]
                        traces.selected.y = [item.z]
                        plot()
                    })
                    d[i].addEventListener("mouseleave",e=>{
                        e.preventDefault();
                        traces.selected.x = []
                        traces.selected.y = []
                        plot()
                    })
                }

                document.getElementById("details").innerHTML = `Translation:<br />
                x: ${pos.translation.x}<br />
                y: ${pos.translation.y}<br />
                z: ${pos.translation.z}<br />
                timestamp: ${pos.timestamp}<br />
                <br />
                Orientation:<br />
                x: ${pos.orientation.x}<br />
                y: ${pos.orientation.y}<br />
                z: ${pos.orientation.z}<br />
                w: ${pos.orientation.w}<br />
                <br />
                Orientation 2:<br />
                roll: ${pos.euler.x}<br />
                pitch: ${pos.euler.y}<br />
                yaw: ${pos.euler.z}<br />
                winkel: ${Math.round(pos.euler.y * 180 / Math.PI,2)}<br />`

            })
    },1000)
}else{
    // const tempData = {"neighbours": [{"id": "1", "color": "blue", "x": 32, "y": 59, "neighbour_same_color": {"distance": 52.773099207835045, "id": "4", "x": 23, "y": 111, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 64.4980619863884, "id": "5", "x": -32, "y": 51, "color": "red", "sameColor": false}}, {"id": "2", "color": "blue", "x": -8, "y": 155, "neighbour_same_color": {"distance": 52.392747589718944, "id": "3", "x": -56, "y": 176, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 78.24321056807422, "id": "6", "x": -57, "y": 94, "color": "red", "sameColor": false}}, {"id": "3", "color": "blue", "x": -56, "y": 176, "neighbour_same_color": {"distance": 52.392747589718944, "id": "2", "x": -8, "y": 155, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 82.00609733428362, "id": "6", "x": -57, "y": 94, "color": "red", "sameColor": false}}, {"id": "4", "color": "blue", "x": 23, "y": 111, "neighbour_same_color": {"distance": 52.773099207835045, "id": "1", "x": 32, "y": 59, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 81.39410298049853, "id": "5", "x": -32, "y": 51, "color": "red", "sameColor": false}}, {"id": "5", "color": "red", "x": -32, "y": 51, "neighbour_same_color": {"distance": 49.73932046178355, "id": "6", "x": -57, "y": 94, "color": "red", "sameColor": true}, "neighbour_other_color": {"distance": 64.4980619863884, "id": "1", "x": 32, "y": 59, "color": "blue", "sameColor": false}}, {"id": "6", "color": "red", "x": -57, "y": 94, "neighbour_same_color": {"distance": 49.73932046178355, "id": "5", "x": -32, "y": 51, "color": "red", "sameColor": true}, "neighbour_other_color": {"distance": 78.24321056807422, "id": "2", "x": -8, "y": 155, "color": "blue", "sameColor": false}}], "route": {"x": 0.0, "y": 55.0, "id": "0", "next": [{"x": -4.5, "y": 81.0, "id": "3", "distance": 26.386549603917523}, {"x": -32.5, "y": 124.5, "id": "1", "distance": 76.72352963726317}, {"x": -56.5, "y": 135.0, "id": "2", "distance": 97.94003267305969}]}, "curve": {"x": [0.0, -0.08, -0.14, -0.18, -0.21, -0.24, -0.25, -0.27, -0.29, -0.31, -0.35, -0.4, -0.46, -0.55, -0.65, -0.79, -0.96, -1.16, -1.41, -1.69, -2.02, -2.41, -2.84, -3.33, -4.5, -4.5, -5.19, -5.96, -6.79, -7.7, -8.66, -9.68, -10.75, -11.86, -13.01, -14.2, -15.42, -16.65, -17.91, -19.18, -20.46, -21.74, -23.02, -24.29, -25.54, -26.78, -27.99, -29.18, -30.33, -32.5, -32.5, -33.55, -34.63, -35.72, -36.82, -37.94, -39.06, -40.19, -41.31, -42.43, -43.54, -44.64, -45.72, -46.78, -47.81, -48.82, -49.8, -50.73, -51.63, -52.49, -53.3, -54.06, -54.76, -55.4], "y": [55.0, 55.55, 56.15, 56.8, 57.5, 58.26, 59.05, 59.9, 60.79, 61.72, 62.69, 63.7, 64.74, 65.83, 66.94, 68.09, 69.27, 70.48, 71.72, 72.98, 74.26, 75.57, 76.9, 78.25, 81.0, 81.0, 82.44, 83.98, 85.62, 87.33, 89.11, 90.95, 92.84, 94.77, 96.74, 98.72, 100.72, 102.72, 104.71, 106.69, 108.64, 110.55, 112.41, 114.22, 115.96, 117.63, 119.21, 120.7, 122.09, 124.5, 124.5, 125.54, 126.49, 127.36, 128.16, 128.88, 129.54, 130.13, 130.67, 131.15, 131.58, 131.97, 132.31, 132.62, 132.89, 133.14, 133.36, 133.57, 133.75, 133.93, 134.1, 134.27, 134.44, 134.61]}, "pylons": {"blue": [{"id": "1", "color": "blue", "x": 32, "y": 59, "distance": 0.0}, {"id": "4", "color": "blue", "x": 23, "y": 111, "distance": 52.773099207835045}, {"id": "2", "color": "blue", "x": -8, "y": 155, "distance": 104.0}, {"id": "3", "color": "blue", "x": -56, "y": 176, "distance": 146.40013661195812}], "red": [{"id": "5", "color": "red", "x": -32, "y": 51, "distance": 0.0}, {"id": "6", "color": "red", "x": -57, "y": 94, "distance": 49.73932046178355}]}, "blueCurved": {"x": [32.0, 31.82, 31.65, 31.48, 31.3, 31.13, 30.95, 30.75, 30.55, 30.34, 30.1, 29.85, 29.58, 29.29, 28.97, 28.62, 28.24, 27.82, 27.37, 26.88, 26.35, 25.78, 25.16, 24.49, 23.0, 23.0, 22.18, 21.31, 20.41, 19.46, 18.48, 17.46, 16.4, 15.3, 14.17, 13.0, 11.8, 10.57, 9.3, 8.01, 6.68, 5.33, 3.94, 2.53, 1.1, -0.36, -1.84, -3.35, -4.88, -8.0, -8.0, -9.64, -11.41, -13.27, -15.24, -17.28, -19.39, -21.56, -23.77, -26.02, -28.28, -30.55, -32.81, -35.06, -37.27, -39.44, -41.55, -43.6, -45.56, -47.43, -49.2, -50.85, -52.36, -53.74], "y": [59.0, 60.13, 61.42, 62.87, 64.47, 66.2, 68.05, 70.01, 72.07, 74.22, 76.44, 78.73, 81.06, 83.44, 85.85, 88.28, 90.71, 93.14, 95.55, 97.94, 100.28, 102.57, 104.8, 106.96, 111.0, 111.0, 112.93, 114.86, 116.8, 118.74, 120.68, 122.62, 124.55, 126.47, 128.38, 130.28, 132.16, 134.02, 135.85, 137.66, 139.44, 141.19, 142.9, 144.58, 146.21, 147.8, 149.34, 150.84, 152.28, 155.0, 155.0, 156.28, 157.52, 158.72, 159.88, 161.01, 162.09, 163.14, 164.15, 165.13, 166.06, 166.97, 167.83, 168.66, 169.46, 170.22, 170.94, 171.63, 172.29, 172.92, 173.51, 174.07, 174.6, 175.1]}, "redCurved": {"x": [-32.0, -32.56, -33.23, -34.0, -34.86, -35.8, -36.81, -37.89, -39.02, -40.19, -41.4, -42.63, -43.88, -45.12, -46.37, -47.6, -48.81, -49.98, -51.11, -52.19, -53.2, -54.14, -55.0, -55.77], "y": [51.0, 51.96, 53.11, 54.43, 55.92, 57.54, 59.28, 61.13, 63.08, 65.09, 67.17, 69.28, 71.43, 73.57, 75.72, 77.83, 79.91, 81.92, 83.87, 85.72, 87.46, 89.08, 90.57, 91.89]}}
    const tempData = {"neighbours": [{"id": "1", "color": "blue", "x": 32, "y": 59, "neighbour_same_color": {"distance": 52.773099207835045, "id": "4", "x": 23, "y": 111, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 64.4980619863884, "id": "5", "x": -32, "y": 51, "color": "red", "sameColor": false}}, {"id": "2", "color": "blue", "x": -8, "y": 155, "neighbour_same_color": {"distance": 52.392747589718944, "id": "3", "x": -56, "y": 176, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 78.24321056807422, "id": "6", "x": -57, "y": 94, "color": "red", "sameColor": false}}, {"id": "3", "color": "blue", "x": -56, "y": 176, "neighbour_same_color": {"distance": 52.392747589718944, "id": "2", "x": -8, "y": 155, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 82.00609733428362, "id": "6", "x": -57, "y": 94, "color": "red", "sameColor": false}}, {"id": "4", "color": "blue", "x": 23, "y": 111, "neighbour_same_color": {"distance": 52.773099207835045, "id": "1", "x": 32, "y": 59, "color": "blue", "sameColor": true}, "neighbour_other_color": {"distance": 81.39410298049853, "id": "5", "x": -32, "y": 51, "color": "red", "sameColor": false}}, {"id": "5", "color": "red", "x": -32, "y": 51, "neighbour_same_color": {"distance": 49.73932046178355, "id": "6", "x": -57, "y": 94, "color": "red", "sameColor": true}, "neighbour_other_color": {"distance": 64.4980619863884, "id": "1", "x": 32, "y": 59, "color": "blue", "sameColor": false}}, {"id": "6", "color": "red", "x": -57, "y": 94, "neighbour_same_color": {"distance": 49.73932046178355, "id": "5", "x": -32, "y": 51, "color": "red", "sameColor": true}, "neighbour_other_color": {"distance": 78.24321056807422, "id": "2", "x": -8, "y": 155, "color": "blue", "sameColor": false}}], "route": {"x": 0.0, "y": 55.0, "id": "0", "next": [{"x": -4.5, "y": 81.0, "id": "3", "distance": 26.386549603917523}, {"x": -32.5, "y": 124.5, "id": "1", "distance": 76.72352963726317}, {"x": -56.5, "y": 135.0, "id": "2", "distance": 97.94003267305969}]}, "curve": {"x": [0.0, -0.3, -4.5, -4.5, -12.24, -32.5, -32.5, -41.69, -56.5], "y": [55.0, 61.09, 81.0, 81.0, 95.43, 124.5, 124.5, 130.83, 135.0]}, "pylons": {"blue": [{"id": "1", "color": "blue", "x": 32, "y": 59, "distance": 0.0}, {"id": "4", "color": "blue", "x": 23, "y": 111, "distance": 52.773099207835045}, {"id": "2", "color": "blue", "x": -8, "y": 155, "distance": 104.0}, {"id": "3", "color": "blue", "x": -56, "y": 176, "distance": 146.40013661195812}], "red": [{"id": "5", "color": "red", "x": -32, "y": 51, "distance": 0.0}, {"id": "6", "color": "red", "x": -57, "y": 94, "distance": 49.73932046178355}]}, "blueCurved": {"x": [32.0, 30.48, 23.0, 23.0, 14.93, -8.0, -8.0, -24.52, -56], "y": [59.0, 72.78, 111.0, 111.0, 127.11, 155.0, 155.0, 164.48, 176]}, "redCurved": {"x": [-32.0, -39.41, -57], "y": [51.0, 63.74, 94]}}
    
    console.log(tempData)

    const driveRoute = {
        x: [tempData.route.x,...tempData.route.next.map(e=>e.x)],
        y: [tempData.route.y,...tempData.route.next.map(e=>e.y)],
        mode: 'lines+markers', // lines+
        type: 'scatter',
        name: "Direct Path",
        active: false,
        line: {
            color: "rgba(255,255,255,.1)",
            width: 1
        },
        marker: {
            color: "#fff",
        },
    }
    
    const interpolatedRoute = {
        x: tempData.curve.x,
        y: tempData.curve.y,
        mode: 'lines+markers',
        type: 'scatter',
        name: "Calculated Path",
        line: {
            color: "#fff"
        },
        marker: {
            color: "transparent"
        },
    }
    
    const bluePylons = {
        x: [...tempData.pylons.blue.map(e=>e.x)],
        y: [...tempData.pylons.blue.map(e=>e.y)],
        mode: 'lines+markers',
        type: 'scatter',
        name: "Blue Pylons",
        line: {
            color: "#0000ff30"
        },
        marker: {
            color: "#0000ff"
        },
    }
    const interpolatedBluePylons = {
        x: tempData.blueCurved.x,
        y: tempData.blueCurved.y,
        mode: 'lines+markers',
        type: 'scatter',
        name: "Blue Outline",
        line: {
            color: "#00f"
        },
        marker: {
            color: "transparent"
        },
    }
    
    const redPylons = {
        x: [...tempData.pylons.red.map(e=>e.x)],
        y: [...tempData.pylons.red.map(e=>e.y)],
        mode: 'lines+markers',
        type: 'scatter',
        name: "Red Pylons",
        line: {
            color: "#ff000030"
        },
        marker: {
            color: "#f00"
        },
    }
    const interpolatedRedPylons = {
        x: tempData.redCurved.x,
        y: tempData.redCurved.y,
        mode: 'lines+markers',
        type: 'scatter',
        name: "Red Outline",
        line: {
            color: "#f00"
        },
        marker: {
            color: "transparent"
        },
    }
    
    const tempReturn = []
    for(let i=0;i<tempData.neighbours.length;i++){
        tempReturn.push({
            x: [tempData.neighbours[i].x,tempData.neighbours[i].neighbour_same_color.x,tempData.neighbours[i].neighbour_other_color.x,tempData.neighbours[i].x],
            y: [tempData.neighbours[i].y,tempData.neighbours[i].neighbour_same_color.y,tempData.neighbours[i].neighbour_other_color.y,tempData.neighbours[i].y],
            mode: 'lines+markers',
            type: 'scatter',
            name: `Triangle ${i+1}`,
            legend: false,
            line: {
                color: "#303030",
                width: 1
            },
            marker: {
                color: "#303030",
            },
        })
    }
    // tempReturn.push(driveRoute)
    Plotly.newPlot('myDiv', [
        ...tempReturn,
        driveRoute,
        interpolatedRoute,
        bluePylons,
        interpolatedBluePylons,
        redPylons,
        interpolatedRedPylons,
    ], {
        width: 500,
        height: 500,
        autoscale: true,
        plot_bgcolor:"transparent",
        paper_bgcolor:"#202020",
        yaxis: {
            tickcolor: "transparent",
            // tickwidth: 15,
            
            gridcolor: "transparent",
            // gridwidth: 15,
            
            zerolinecolor: "green",
            // zerolinewidth: 2,
        },
        xaxis: {
            tickcolor: "transparent",
            // tickwidth: 50,
            
            gridcolor: "transparent",
            // gridwidth: 2,      
        }
    });
}