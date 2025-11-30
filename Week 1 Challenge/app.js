const { DateTime } = luxon;

// Target timezones for conversion
const TARGET_TIMEZONES = [
    { name: 'US Pacific', zone: 'America/Los_Angeles', region: 'Americas' },
    { name: 'US Mountain', zone: 'America/Denver', region: 'Americas' },
    { name: 'US Central', zone: 'America/Chicago', region: 'Americas' },
    { name: 'US Eastern', zone: 'America/New_York', region: 'Americas' },
    { name: 'Toronto', zone: 'America/Toronto', region: 'Americas' },
    { name: 'Mexico City', zone: 'America/Mexico_City', region: 'Americas' },
    { name: 'São Paulo', zone: 'America/Sao_Paulo', region: 'Americas' },
    { name: 'London', zone: 'Europe/London', region: 'Europe' },
    { name: 'Paris', zone: 'Europe/Paris', region: 'Europe' },
    { name: 'Berlin', zone: 'Europe/Berlin', region: 'Europe' },
    { name: 'Amsterdam', zone: 'Europe/Amsterdam', region: 'Europe' },
    { name: 'Stockholm', zone: 'Europe/Stockholm', region: 'Europe' },
    { name: 'Moscow', zone: 'Europe/Moscow', region: 'Europe' },
    { name: 'Dubai', zone: 'Asia/Dubai', region: 'Middle East & Asia' },
    { name: 'India', zone: 'Asia/Kolkata', region: 'Middle East & Asia' },
    { name: 'Singapore', zone: 'Asia/Singapore', region: 'Middle East & Asia' },
    { name: 'Hong Kong', zone: 'Asia/Hong_Kong', region: 'Middle East & Asia' },
    { name: 'Tokyo', zone: 'Asia/Tokyo', region: 'Middle East & Asia' },
    { name: 'Seoul', zone: 'Asia/Seoul', region: 'Middle East & Asia' },
    { name: 'Sydney', zone: 'Australia/Sydney', region: 'Pacific' },
    { name: 'Melbourne', zone: 'Australia/Melbourne', region: 'Pacific' },
    { name: 'Auckland', zone: 'Pacific/Auckland', region: 'Pacific' }
];

// Date format options
const DATE_FORMATS = {
  full: { label: 'Full (Tuesday, Nov 30, 2024)', format: 'EEEE, LLL dd, yyyy' },
  short: { label: 'Short (11/30/2024)', format: 'MM/dd/yyyy' },
  iso: { label: 'ISO (2024-11-30)', format: 'yyyy-MM-dd' },
  european: { label: 'European (30/11/2024)', format: 'dd/MM/yyyy' }
};

// Common timezones for the selector
const COMMON_TIMEZONES = [
    { name: 'US Pacific (Los Angeles)', zone: 'America/Los_Angeles' },
    { name: 'US Mountain (Denver)', zone: 'America/Denver' },
    { name: 'US Central (Chicago)', zone: 'America/Chicago' },
    { name: 'US Eastern (New York)', zone: 'America/New_York' },
    { name: 'Toronto', zone: 'America/Toronto' },
    { name: 'Mexico City', zone: 'America/Mexico_City' },
    { name: 'São Paulo', zone: 'America/Sao_Paulo' },
    { name: 'Buenos Aires', zone: 'America/Argentina/Buenos_Aires' },
    { name: 'London', zone: 'Europe/London' },
    { name: 'Paris', zone: 'Europe/Paris' },
    { name: 'Berlin', zone: 'Europe/Berlin' },
    { name: 'Amsterdam', zone: 'Europe/Amsterdam' },
    { name: 'Stockholm', zone: 'Europe/Stockholm' },
    { name: 'Moscow', zone: 'Europe/Moscow' },
    { name: 'Istanbul', zone: 'Europe/Istanbul' },
    { name: 'Dubai', zone: 'Asia/Dubai' },
    { name: 'India (Kolkata)', zone: 'Asia/Kolkata' },
    { name: 'Bangkok', zone: 'Asia/Bangkok' },
    { name: 'Singapore', zone: 'Asia/Singapore' },
    { name: 'Hong Kong', zone: 'Asia/Hong_Kong' },
    { name: 'Shanghai', zone: 'Asia/Shanghai' },
    { name: 'Tokyo', zone: 'Asia/Tokyo' },
    { name: 'Seoul', zone: 'Asia/Seoul' },
    { name: 'Sydney', zone: 'Australia/Sydney' },
    { name: 'Melbourne', zone: 'Australia/Melbourne' },
    { name: 'Auckland', zone: 'Pacific/Auckland' }
];

// State
let currentDateTime = null;
let currentSourceTimezone = null;
let selectedDateFormat = 'full';

// Initialize the app
function init() {
    populateTimezoneSelector();
    populateDateFormatSelector();
    setDefaultDateTime();
    checkURLParams();
    
    document.getElementById('timeForm').addEventListener('submit', handleFormSubmit);
    document.getElementById('copyAllBtn').addEventListener('click', copyAllTimes);
    document.getElementById('newConversionBtn').addEventListener('click', showForm);
    document.getElementById('exportCalendarBtn').addEventListener('click', exportToCalendar);
    document.getElementById('dateFormatSelect').addEventListener('change', handleDateFormatChange);
}

// Populate timezone selector with options
function populateTimezoneSelector() {
    const select = document.getElementById('timezoneInput');
    const userTimezone = DateTime.local().zoneName;
    
    COMMON_TIMEZONES.forEach(tz => {
        const option = document.createElement('option');
        option.value = tz.zone;
        option.textContent = tz.name;
        if (tz.zone === userTimezone) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

// Populate date format selector
function populateDateFormatSelector() {
    const select = document.getElementById('dateFormatSelect');
    Object.entries(DATE_FORMATS).forEach(([key, value]) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = value.label;
        select.appendChild(option);
    });
}

// Handle date format change
function handleDateFormatChange(e) {
    selectedDateFormat = e.target.value;
    if (currentDateTime && currentSourceTimezone) {
        displayResults(currentDateTime, currentSourceTimezone);
    }
}

// Set default date and time to now
function setDefaultDateTime() {
    const now = DateTime.local();
    document.getElementById('dateInput').value = now.toISODate();
    document.getElementById('timeInput').value = now.toFormat('HH:mm');
}

// Check if URL has parameters and show results
function checkURLParams() {
    const params = new URLSearchParams(window.location.search);
    const time = params.get('time');
    const tz = params.get('tz');
    
    if (time && tz) {
        try {
            const dt = DateTime.fromISO(time, { zone: tz });
            if (dt.isValid) {
                displayResults(dt, tz);
            }
        } catch (e) {
            console.error('Invalid URL parameters:', e);
        }
    }
}

// Handle form submission
function handleFormSubmit(e) {
    e.preventDefault();
    
    const date = document.getElementById('dateInput').value;
    const time = document.getElementById('timeInput').value;
    const timezone = document.getElementById('timezoneInput').value;
    
    const dateTimeString = `${date}T${time}`;
    const dt = DateTime.fromISO(dateTimeString, { zone: timezone });
    
    if (!dt.isValid) {
        showToast('Invalid date or time. Please check your inputs.', 'error');
        return;
    }
    
    // Update URL
    const url = new URL(window.location);
    url.searchParams.set('time', dt.toISO());
    url.searchParams.set('tz', timezone);
    window.history.pushState({}, '', url);
    
    displayResults(dt, timezone);
}

// Display conversion results
function displayResults(sourceDateTime, sourceTimezone) {
    currentDateTime = sourceDateTime;
    currentSourceTimezone = sourceTimezone;
    
    const timesList = document.getElementById('timesList');
    timesList.innerHTML = '';
    
    // Group by region
    const regions = {};
    TARGET_TIMEZONES.forEach(tz => {
        if (!regions[tz.region]) {
            regions[tz.region] = [];
        }
        regions[tz.region].push(tz);
    });
    
    // Create region sections
    Object.entries(regions).forEach(([region, timezones]) => {
        const regionHeader = document.createElement('div');
        regionHeader.className = 'region-header';
        regionHeader.textContent = region;
        timesList.appendChild(regionHeader);
        
        timezones.forEach(tz => {
            const converted = sourceDateTime.setZone(tz.zone);
            const timeCard = createTimeCard(tz.name, converted);
            timesList.appendChild(timeCard);
        });
    });
    
    document.getElementById('converterForm').classList.add('hidden');
    document.getElementById('resultsDisplay').classList.remove('hidden');
}

// Create a time card element
function createTimeCard(timezoneName, dateTime) {
    const card = document.createElement('div');
    card.className = 'time-card';
    
    const dateFormat = DATE_FORMATS[selectedDateFormat].format;
    const formattedDate = dateTime.toFormat(dateFormat);
    const formattedTime = dateTime.toFormat('h:mm a ZZZZ');
    const fullText = `${formattedDate} at ${formattedTime}`;
    
    card.innerHTML = `
        <div class="time-info">
            <div class="time-zone">${timezoneName}</div>
            <div class="time-value">${fullText}</div>
        </div>
        <button class="time-copy-btn" onclick="copyTime(\`${fullText.replace(/`/g, '\\`')}\`)">
            Copy
        </button>
    `;
    
    return card;
}

// Copy single time to clipboard
function copyTime(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// Copy all times to clipboard
function copyAllTimes() {
    const allTimes = getAllTimesText();
    
    navigator.clipboard.writeText(allTimes).then(() => {
        showToast('All times copied to clipboard');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Show form and reset URL
function showForm() {
    document.getElementById('resultsDisplay').classList.add('hidden');
    document.getElementById('converterForm').classList.remove('hidden');
    window.history.pushState({}, '', window.location.pathname);
}

// Export to calendar (ICS format)
function exportToCalendar() {
    if (!currentDateTime || !currentSourceTimezone) return;
    
    // Create ICS content
    const icsContent = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Meeting Timezone Converter//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        `DTSTART:${currentDateTime.toFormat("yyyyMMdd'T'HHmmss")}`,
        `DTEND:${currentDateTime.plus({ hours: 1 }).toFormat("yyyyMMdd'T'HHmmss")}`,
        `DTSTAMP:${DateTime.now().toFormat("yyyyMMdd'T'HHmmss'Z'")}`,
        'UID:' + Date.now() + '@meetingtimezone.app',
        'SUMMARY:Meeting',
        'DESCRIPTION:Meeting scheduled across timezones\\n\\n' + getAllTimesText().replace(/\n/g, '\\n'),
        'STATUS:CONFIRMED',
        'SEQUENCE:0',
        'END:VEVENT',
        'END:VCALENDAR'
    ].join('\r\n');
    
    // Create download link
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'meeting.ics';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Calendar event downloaded');
}

// Get all times as text
function getAllTimesText() {
    const timesList = document.getElementById('timesList');
    return Array.from(timesList.children)
        .filter(el => !el.classList.contains('region-header'))
        .map(card => {
            const timezone = card.querySelector('.time-zone')?.textContent || '';
            const datetime = card.querySelector('.time-value')?.textContent || '';
            return `${timezone}: ${datetime}`;
        })
        .join('\n');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
