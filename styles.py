import pygal
from pygal.style import Style

histo_style_2_sets = Style(
  background='transparent',
  plot_background='transparent',
  #foreground='#333',
  #foreground_strong='#333',
  #foreground_subtle='#333',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  colors=('#FF2222', '#E02233', '#2233EC', '#3353EC', '#E89B53'))


if __name__ == '__main__':
	chart = pygal.StackedLine(fill=True, interpolate='cubic', style=custom_style)
	chart.add('A', [1, 3,  5, 16, 13, 3,  7])
	chart.add('B', [5, 2,  3,  2,  5, 7, 17])
	chart.add('C', [6, 10, 9,  7,  3, 1,  0])
	chart.add('D', [2,  3, 5,  9, 12, 9,  5])
	chart.add('E', [7,  4, 2,  1,  2, 10, 0])
	chart.render()
