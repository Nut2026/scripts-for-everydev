/**
 * This is an Apps Script for Google Sheets.
 * 
 * It automatically records the date (column A) and timestamp (column B) whenever
 * you type something into column C of the same row.
 *
 * Column A  ->  Date + day-of-week  (written only on the first entry of a new day)
 * Column B  ->  Time                (written on every entry)
 * Column C  ->  User input          (when written, triggers Column A & B)
 *
 * IMPORTANT: 
 * - A column B is written with every column C, but column A is only written
 * when the days are different, i.e. you can only ever see one "15-10-10 (Thu)."
 * - Row 1 is reserved as the header row. The script intentionally skips row 1 edits. As such, edits on the first row will not trigger
 * any auto-logging. Please begin your logging on row 2.
 * 
 * To use, please:
 * 1. Change the sheet tab name in Line 41 (currently placeholder as "Sheets 1") to the sheet tab you're working on. 
 * 
 * Watch it work and enjoy! Feel free to customise the script to fit your 
 * 
 * Usage examples: Manual logging, journalling, or when you'd like to watch your
 * ideas evolve over hours.
 * 
 * Example Output:
 * 
 *   |  A (Date)         |  B (Time)  |  C (Your input)    |
 *   |-------------------|------------|--------------------|
 *   |  2026-10-15 (Thu) |  09:14:02  |  first task        |
 *   |                   |  11:32:47  |  second task       |
 *   |                   |  15:08:11  |  third task        |
 *   |  2026-10-16 (Fri) |  08:45:20  |  next-day task     |
 *   |                   |  10:20:05  |  another task      |
 *   |  2026-10-17 (Sat) |  22:01:33  |  new day again     |
 * 
 */

function onEdit(e) {
  var sheet = e.source.getActiveSheet();
  var range = e.range;
  var col = range.getColumn();
  var row = range.getRow();

  if (sheet.getName() !== "Sheets 1") return;

  if (col !== 3 || row === 1) return;

  var now = new Date();
  var tz = Session.getScriptTimeZone();

  var timeCell = sheet.getRange(row, 2);
  if (range.getValue() === "") {
    timeCell.clearContent();
  } else {
    timeCell.setValue(Utilities.formatDate(now, tz, "HH:mm:ss"));
  }

  var dateCell = sheet.getRange(row, 1);
  if (range.getValue() === "") {
    dateCell.clearContent();
    return;
  }

  var lastDateStr = "";
  if (row > 2) {
    var above = sheet.getRange(2, 1, row - 2, 1).getValues();
    for (var i = above.length - 1; i >= 0; i--) {
      if (above[i][0] !== "") {
        lastDateStr = above[i][0].toString();
        break;
      }
    }
  }

  var todayStr = Utilities.formatDate(now, tz, "yyyy-MM-dd (EEE)");

  if (lastDateStr !== todayStr) {
    dateCell.setValue(todayStr);
  } else {
    dateCell.clearContent();
  }
}
