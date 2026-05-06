Make an application for a recurring lottery.

* Tech
  * Maintain a MVC architecture
  * All parameters in a config file.
  * Qt based

* Basics
  *  Those eligeble for the lottery are defined in an excel file.
  * Each lottery has at it’s start a list of prizes, and at its finish a list of winners. This is defined and saved in a folder with today’s date. The prizes are pieces of art, (about 20) represented by a picture and a text.
 * A winner is drawn from the list of eligible with one exception  
 * You can only win once per lottery occasion. 
 * The exception: the winners of the previous lottery (which had at the earlier instance been saved in a folder with the last date before today’s) is exempt from the first three wins. After the third win they participate on equal terms as the other.

 * If the winner is present at the lottery the winner selects a prize. 
 * If the winner is not present the drawing is redone. 
 * Repeat drawings until there are no prizes left. Thus, there are at least as many drawings as there are prizes, but there may be more. 
 * The list of winners are saved in the folder with today’s date (see above)



* The gui:
  * Show the prizes in a grid.
  * Button: “DRAW!” that initiates the drawing, and presents the winners name. After DRAW is clicked it is disabled and will be enabled when “confirm” or “not present” is clicked.
  * Button: "Confirm". The winner is confirmed when a “confirm” button is clicked.
  * Button: "Not present" If the winner is not present a ”not present” button is clicked 
  * The winners choice is done by clicking one of the remaining prizes. It's image then goes grey and can not be selected anymore. Note that the prize selection is manual.
* Records
  * Update a list of winners and their prize selection in the gui and saved to the folder for today’s lottery. Saving format is always excel.

Create mock data 100 participants and 20 art images pulled from the internet or similar.