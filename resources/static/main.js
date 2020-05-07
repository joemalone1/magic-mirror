var reminderIdx = 0;

window.onload = function() {
    setBackground(background)
    setReminder(daily_reminders[0])
    setTime()
    setInterval(setTime, 5000)
    setInterval(changeReminder, 5000)
}

// TODO: Call setReminder on a timer to rotate among all daily reminders

function setBackground(background) {
	var backDiv = document.getElementsByClassName("below")
    var bkgdImg = document.createElement("img")

    bkgdImg.setAttribute("src", background)
    bkgdImg.style.opacity = 0.3
    bkgdImg.style.width = 100%
    backDiv[0].appendChild(bkgdImg)
}

function setReminder(reminder) {
	var reminderTag = document.getElementById("daily_reminder")
	reminderTag.textContent = reminder
}

function changeReminder() {
	var reminderTag = document.getElementById("daily_reminder")
	reminderIdx = reminderIdx + 1 < daily_reminders.length ? reminderIdx + 1 : 0;
	reminderTag.textContent = daily_reminders[reminderIdx]

}

function setTime() {
	var today = new Date();
	var monthMap = {
		0:"January",
		1:"February",
		2:"March",
		3:"April",
		4:"May",
		5:"June",
		6:"July",
		7:"August",
		8:"September",
		9:"October",
		10:"November",
		11:"December"
	}
	var dayMap = {
		0:"Sunday",
		1:"Monday",
		2:"Tuesday",
		3:"Wednesday",
		4:"Thursday",
		5:"Friday",
		6:"Saturday"
	}
	var hours = today.getHours();
	hours = hours < 10 ? "0" + hours : hours;
	var minutes = today.getMinutes();
	minutes = minutes < 10 ? "0" + minutes : minutes;
	var time = hours + ":" + minutes;
	var date = dayMap[today.getDay()] + ", " + monthMap[today.getMonth()] + " " + today.getDate();
	document.getElementById("time").textContent = time;
	document.getElementById("date").textContent = date;
}