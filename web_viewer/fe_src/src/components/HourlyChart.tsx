import {
  ForwardedRef,
  forwardRef,
  memo,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import "./HourlyChart.css";
import Chart from "react-apexcharts";
import { IClassNameProps, IUpdateChart, SeriesItem } from "../Intefaces";

const HourlyChart = forwardRef(({ className }: IClassNameProps, ref: ForwardedRef<IUpdateChart>) => {
  const [chartData, setChartData] = useState<never[][]>([]);
  const [isDark, setIsDark] = useState(false);
  const isFetchingRef = useRef<boolean>(false);

  const series = useMemo(() => {
    const pvSeries: SeriesItem[] = [];
    const batterySeries: SeriesItem[] = [];
    const gridSeries: SeriesItem[] = [];
    const consumptionSeries: SeriesItem[] = [];
    const socSeries: SeriesItem[] = [];

    chartData.forEach((item) => {
      const time = new Date(item[1]).getTime();
      pvSeries.push({ x: time, y: item[2] });
      batterySeries.push({ x: time, y: item[3] });
      gridSeries.push({ x: time, y: item[4] });
      consumptionSeries.push({ x: time, y: item[5] });
      socSeries.push({ x: time, y: item[6] });
    });
    return [
      {
        name: "PV",
        data: pvSeries,
      },
      {
        name: "Battery",
        data: batterySeries,
      },
      {
        name: "Grid",
        data: gridSeries,
      },
      {
        name: "Consumption",
        data: consumptionSeries,
      },
      {
        name: "SOC",
        data: socSeries,
      },
    ];
  }, [chartData]);

  const fetchChart = useCallback(async () => {
    if (isFetchingRef.current) {
      return;
    }
    isFetchingRef.current = true;
    const res = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/hourly-chart`
    );
    const json = await res.json();
    setChartData(json);
    isFetchingRef.current = false;
  }, [setChartData]);

  useImperativeHandle(ref, (): IUpdateChart => ({
    updateItem(hourlyItem) {
      const lastItem = chartData[chartData.length - 1];
      if (JSON.stringify(lastItem) === JSON.stringify(hourlyItem)) {
        return;
      }
      const newChartData = [...chartData];
      if (lastItem[0] === hourlyItem[0]) {
        newChartData.splice(chartData.length - 1, 1, hourlyItem);
      } else {
        newChartData.push(hourlyItem);
      }
      setChartData(newChartData);
    },
  }));

  useEffect(() => {
    fetchChart();
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) {
        fetchChart();
      }
    });
  }, [fetchChart, ref]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");

    if (mq.matches) {
      setIsDark(true);
    }

    // This callback will fire if the perferred color scheme changes without a reload
    mq.addEventListener("change", (evt) => setIsDark(evt.matches));
  }, []);

  return (
    <div className={`card hourly-chart ${className || ""}`}>
      <div className="row justify-space-between">
        <div className="hourly-chart-title">Hourly Chart</div>
        <div className="row">
          <button onClick={() => fetchChart()}>Update</button>
        </div>
      </div>
      <div className="hourly-chart-content">
        <Chart
          type="line"
          series={series}
          options={{
            chart: {
              toolbar: {
                show: false,
              },
              height: 300,
            },
            colors: [
              "rgb(112, 173, 70)",
              "rgb(90, 155, 213)",
              "rgb(246, 104, 103)",
              "rgb(255, 164, 97)",
              "rgb(128, 0, 128)",
            ],
            stroke: {
              width: 3,
            },
            theme: {
              mode: isDark ? "dark" : "light",
            },
            xaxis: {
              type: "datetime",
              labels: {
                datetimeUTC: false,
              },
            },
            yaxis: [
              { seriesName: "PV", title: { text: "Power (W)" } },
              { seriesName: "PV", show: false },
              { seriesName: "PV", show: false },
              { seriesName: "PV", show: false },
              {
                seriesName: "SOC",
                opposite: true,
                tickAmount: 10,
                min: 0,
                max: 100,
                title: {
                  text: "SOC (%)",
                },
              },
            ],
            tooltip: {
              x: {
                format: "HH:mm:ss",
              },
              y: {
                formatter(val, opts) {
                  if (opts.seriesIndex === 4) {
                    return `${val}%`;
                  }
                  return `${val} W`;
                },
              },
            },
          }}
        />
      </div>
    </div>
  );
});

HourlyChart.displayName = "HourlyChart";

export default memo(HourlyChart);
