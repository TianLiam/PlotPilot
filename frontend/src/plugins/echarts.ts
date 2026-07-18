import { use } from 'echarts/core'
import {
  BarChart,
  LineChart,
  PieChart,
  GraphChart,
  HeatmapChart,
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  MarkPointComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// Keep the registry aligned with actual chart usage to avoid shipping unused ECharts modules.
use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  MarkPointComponent,
  VisualMapComponent,
  BarChart,
  LineChart,
  PieChart,
  GraphChart,
  HeatmapChart,
  CanvasRenderer
])

