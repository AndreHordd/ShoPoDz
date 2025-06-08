import initSidebar from './init.js';
import {fetchPanel} from './fetch.js';
import {renderSchedule} from './renderSchedule.js';
import {renderHomework} from './renderHomework.js';
import {renderTeachers} from './renderTeachers.js';
import {renderAttendance} from './renderAttendance.js';
import {renderAnnouncements} from './renderAnnouncements.js';
import {inject, tableMarkup, getVal} from './utils.js';

window.inject = inject;
window.tableMarkup = tableMarkup;
window.getVal = getVal;

const renderers = {
    schedule:      renderSchedule,
    homework:      renderHomework,
    teachers:      renderTeachers,
    attendance:    renderAttendance,
    announcements: renderAnnouncements,
};

initSidebar(renderers, fetchPanel);
