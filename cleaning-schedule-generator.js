(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && root.document) api.init(root.document, root);
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  var FREQUENCIES = {
    'after-use': 'After use', shift: 'Each shift', daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly'
  };
  var MAX_TASKS = 30;
  var DEFAULT_TASKS = [
    { name: 'Work surfaces and chopping boards', frequency: 'after-use', when: 'Between tasks and after handling raw food', responsible: '', product: '', contact: '', method: '' },
    { name: 'Handles, taps and touch points', frequency: 'daily', when: 'Review during the shift', responsible: '', product: '', contact: '', method: '' },
    { name: 'Floors and waste areas', frequency: 'daily', when: 'Clean spills as they happen', responsible: '', product: '', contact: '', method: '' },
    { name: 'Fridge shelves and seals', frequency: 'weekly', when: 'Set a day; deal with spills immediately', responsible: '', product: '', contact: '', method: '' }
  ];

  function createDefaultTasks() {
    return DEFAULT_TASKS.map(function (task, index) { return Object.assign({ id: index + 1 }, task); });
  }

  function parseISODate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    var parts = value.split('-').map(Number);
    if (parts[0] < 1900 || parts[0] > 9999) return null;
    var date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    return date.getUTCFullYear() === parts[0] && date.getUTCMonth() === parts[1] - 1 && date.getUTCDate() === parts[2] ? date : null;
  }

  function currentMonday(now) {
    var date = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
    date.setUTCDate(date.getUTCDate() - (date.getUTCDay() + 6) % 7);
    return date.toISOString().slice(0, 10);
  }

  function weekDates(value) {
    var first = parseISODate(value);
    if (!first) return [];
    var dates = [];
    for (var i = 0; i < 7; i++) {
      var date = new Date(first.getTime());
      date.setUTCDate(first.getUTCDate() + i);
      dates.push({
        iso: date.toISOString().slice(0, 10),
        day: date.toLocaleDateString('en-GB', { weekday: 'short', timeZone: 'UTC' }),
        short: date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' }),
        full: date.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
      });
    }
    return dates;
  }

  function validateTasks(tasks) {
    if (!Array.isArray(tasks) || !tasks.length) return 'Add at least one cleaning job before printing or exporting.';
    if (tasks.length > MAX_TASKS) return 'Use no more than ' + MAX_TASKS + ' jobs in one schedule.';
    for (var i = 0; i < tasks.length; i++) {
      if (!String(tasks[i].name || '').trim()) return 'Enter a name for job ' + (i + 1) + ' before printing or exporting.';
      if (!Object.prototype.hasOwnProperty.call(FREQUENCIES, tasks[i].frequency)) return 'Choose a frequency for job ' + (i + 1) + '.';
    }
    return '';
  }

  function csvCell(value) {
    var text = String(value == null ? '' : value);
    // Spreadsheet apps can interpret a leading formula even after spaces or tabs.
    if (/^[\s\u0000-\u001f]*[=+\-@]/.test(text)) text = "'" + text;
    return '"' + text.replace(/"/g, '""') + '"';
  }

  function makeCSV(business, date, tasks) {
    var error = validateTasks(tasks);
    if (error) throw new Error(error);
    var days = weekDates(date);
    if (!days.length) throw new Error('Choose a valid week commencing date before exporting.');
    var rows = [['Kitchen', 'Week commencing', 'Cleaning job', 'Frequency', 'When', 'Responsible', 'Product', 'Contact time', 'Method'].concat(days.map(function (day) { return day.day + ' ' + day.iso + ' initials'; }))];
    tasks.forEach(function (task) {
      rows.push([business, date, task.name, FREQUENCIES[task.frequency], task.when, task.responsible, task.product, task.contact, task.method].concat(['', '', '', '', '', '', '']));
    });
    return '\ufeff' + rows.map(function (row) { return row.map(csvCell).join(','); }).join('\r\n') + '\r\n';
  }

  function init(doc, win) {
    var generator = doc.getElementById('generator');
    if (!generator) return;
    var list = doc.getElementById('task-list');
    var business = doc.getElementById('business-name');
    var date = doc.getElementById('week-start');
    var addForm = doc.getElementById('add-task-form');
    var newName = doc.getElementById('new-task-name');
    var newFrequency = doc.getElementById('new-task-frequency');
    var addError = doc.getElementById('add-task-error');
    var exportError = doc.getElementById('export-error');
    var printButton = doc.getElementById('print-schedule');
    var exportButton = doc.getElementById('export-schedule');
    var undoButton = doc.getElementById('undo-remove');
    var status = doc.getElementById('generator-status');
    var state = { tasks: createDefaultTasks(), nextId: 5, removed: null };

    function element(tag, attrs, text) {
      var node = doc.createElement(tag);
      Object.keys(attrs || {}).forEach(function (key) { node.setAttribute(key, attrs[key]); });
      if (text != null) node.textContent = text;
      return node;
    }

    function announce(text) { status.textContent = text; }
    function showError(node, text) { node.textContent = text; node.hidden = !text; }
    function track(name) {
      try { if (typeof win.gtag === 'function') win.gtag('event', name); } catch (error) {}
    }

    function inputField(task, field, label, options) {
      options = options || {};
      var box = element('div', options.wide ? { 'class': 'wide' } : {});
      var id = 'task-' + task.id + '-' + field;
      box.appendChild(element('label', { 'for': id }, label));
      var attrs = { id: id, 'data-task-id': task.id, 'data-field': field, maxlength: options.maxlength || 100, 'aria-label': label + ' for job ' + task.id };
      if (options.placeholder) attrs.placeholder = options.placeholder;
      var input = element(options.multiline ? 'textarea' : 'input', attrs);
      if (!options.multiline) input.type = 'text';
      if (field === 'name') input.required = true;
      input.value = task[field] || '';
      box.appendChild(input);
      return box;
    }

    function frequencyField(task) {
      var box = element('div');
      var id = 'task-' + task.id + '-frequency';
      box.appendChild(element('label', { 'for': id }, 'Frequency'));
      var select = element('select', { id: id, 'data-task-id': task.id, 'data-field': 'frequency', 'aria-label': 'Frequency for job ' + task.id });
      Object.keys(FREQUENCIES).forEach(function (value) { var option = element('option', { value: value }, FREQUENCIES[value]); option.selected = task.frequency === value; select.appendChild(option); });
      box.appendChild(select);
      return box;
    }

    function renderEditor() {
      list.replaceChildren();
      state.tasks.forEach(function (task, index) {
        var card = element('div', { 'class': 'task-card' });
        var fieldset = element('fieldset');
        fieldset.appendChild(element('legend', {}, 'Job ' + (index + 1)));
        var primary = element('div', { 'class': 'task-primary' });
        primary.appendChild(inputField(task, 'name', 'Cleaning job', { maxlength: 120 }));
        primary.appendChild(frequencyField(task));
        primary.appendChild(element('button', { type: 'button', 'class': 'remove-button', 'data-remove': task.id, 'aria-label': 'Remove job ' + (index + 1) }, 'Remove'));
        fieldset.appendChild(primary);
        var details = element('details', { 'class': 'task-details' });
        details.appendChild(element('summary', {}, 'Method, product and responsibility'));
        var extra = element('div', { 'class': 'task-extra' });
        extra.appendChild(inputField(task, 'when', 'When / trigger', { placeholder: 'e.g. After use; Sunday; first Monday' }));
        extra.appendChild(inputField(task, 'responsible', 'Who is responsible?', { placeholder: 'e.g. Closing team' }));
        extra.appendChild(inputField(task, 'product', 'Cleaning product', { placeholder: 'Use the name on the label' }));
        extra.appendChild(inputField(task, 'contact', 'Contact time / dilution', { placeholder: "Follow the manufacturer's instructions" }));
        extra.appendChild(inputField(task, 'method', 'Cleaning method and precautions', { multiline: true, wide: true, maxlength: 500, placeholder: 'Write your agreed method and any equipment precautions.' }));
        details.appendChild(extra);
        fieldset.appendChild(details);
        card.appendChild(fieldset);
        list.appendChild(card);
      });
      undoButton.hidden = !state.removed;
    }

    function renderPreview() {
      var days = weekDates(date.value);
      doc.getElementById('preview-business').textContent = business.value.trim() || 'Your kitchen';
      doc.getElementById('preview-week').textContent = days.length ? days[0].full + ' – ' + days[6].full : 'Choose a valid week commencing date above.';
      var head = doc.getElementById('schedule-head');
      var row = element('tr');
      row.appendChild(element('th', { scope: 'col' }, 'Job and method'));
      row.appendChild(element('th', { scope: 'col' }, 'Frequency'));
      var headers = days.length ? days : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(function (day) { return { day: day, short: '' }; });
      headers.forEach(function (day) { var th = element('th', { scope: 'col', 'class': 'day' }, day.day); th.appendChild(element('span', {}, day.short)); row.appendChild(th); });
      head.replaceChildren(row);
      var body = doc.getElementById('schedule-body');
      body.replaceChildren();
      state.tasks.forEach(function (task, index) {
        var tr = element('tr');
        var description = element('th', { scope: 'row', 'class': 'task-description' });
        description.appendChild(element('strong', {}, task.name.trim() || 'Job ' + (index + 1) + ': add a name'));
        if (task.method.trim()) description.appendChild(element('span', {}, task.method));
        [['When: ', task.when], ['Responsible: ', task.responsible], ['Product: ', task.product], ['Contact / dilution: ', task.contact]].forEach(function (pair) { if (String(pair[1] || '').trim()) description.appendChild(element('span', { 'class': 'task-meta' }, pair[0] + pair[1])); });
        tr.appendChild(description);
        tr.appendChild(element('td', { 'class': 'frequency-cell' }, FREQUENCIES[task.frequency] || 'Choose frequency'));
        for (var day = 0; day < 7; day++) tr.appendChild(element('td', { 'class': 'completion' }));
        body.appendChild(tr);
      });
      if (!state.tasks.length) { var empty = element('tr'); empty.appendChild(element('td', { colspan: 9, 'class': 'empty-row' }, 'Add a cleaning job above to start your schedule.')); body.appendChild(empty); }
    }

    function validateForExport() {
      var message = validateTasks(state.tasks);
      date.setAttribute('aria-invalid', String(!parseISODate(date.value)));
      state.tasks.forEach(function (task) { var input = doc.getElementById('task-' + task.id + '-name'); if (input) input.setAttribute('aria-invalid', String(!task.name.trim())); });
      if (message) {
        showError(exportError, message);
        var blank = state.tasks.find(function (task) { return !task.name.trim(); });
        if (blank) doc.getElementById('task-' + blank.id + '-name').focus(); else newName.focus();
        return false;
      }
      if (!parseISODate(date.value)) { showError(exportError, 'Choose a valid week commencing date before printing or exporting.'); date.focus(); return false; }
      showError(exportError, '');
      renderPreview();
      return true;
    }

    list.addEventListener('input', function (event) {
      var input = event.target;
      if (!input.dataset || !input.dataset.field) return;
      var task = state.tasks.find(function (item) { return item.id === Number(input.dataset.taskId); });
      if (!task) return;
      task[input.dataset.field] = input.value;
      if (input.dataset.field === 'name') input.setAttribute('aria-invalid', String(!input.value.trim()));
      showError(exportError, '');
      renderPreview();
    });

    list.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-remove]');
      if (!button) return;
      var index = state.tasks.findIndex(function (task) { return task.id === Number(button.dataset.remove); });
      if (index < 0) return;
      var removed = state.tasks.splice(index, 1)[0];
      state.removed = { task: removed, index: index };
      renderEditor();
      renderPreview();
      showError(exportError, '');
      announce((removed.name || 'Job') + ' removed. You can undo this removal.');
      undoButton.focus();
    });

    undoButton.addEventListener('click', function () {
      if (!state.removed) return;
      if (state.tasks.length >= MAX_TASKS) { announce('Remove a job before restoring another. The limit is ' + MAX_TASKS + '.'); return; }
      var removed = state.removed;
      state.tasks.splice(Math.min(removed.index, state.tasks.length), 0, removed.task);
      state.removed = null;
      renderEditor();
      renderPreview();
      announce('Job restored.');
      doc.getElementById('task-' + removed.task.id + '-name').focus();
    });

    addForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var name = newName.value.trim();
      if (!name) { showError(addError, 'Enter a cleaning job to add.'); newName.setAttribute('aria-invalid', 'true'); newName.focus(); return; }
      if (state.tasks.length >= MAX_TASKS) { showError(addError, 'This sheet supports up to ' + MAX_TASKS + ' jobs. Remove a job before adding another.'); return; }
      var id = state.nextId++;
      state.tasks.push({ id: id, name: name, frequency: newFrequency.value, when: '', responsible: '', product: '', contact: '', method: '' });
      newName.value = '';
      newName.setAttribute('aria-invalid', 'false');
      showError(addError, '');
      showError(exportError, '');
      renderEditor();
      renderPreview();
      announce(name + ' added. ' + state.tasks.length + ' jobs in your schedule.');
      doc.getElementById('task-' + id + '-name').focus();
    });

    newName.addEventListener('input', function () { newName.setAttribute('aria-invalid', 'false'); showError(addError, ''); });
    business.addEventListener('input', renderPreview);
    date.addEventListener('input', function () { date.setAttribute('aria-invalid', String(!parseISODate(date.value))); showError(exportError, ''); renderPreview(); });
    printButton.addEventListener('click', function () {
      if (!validateForExport()) return;
      try { win.print(); track('cleaning_schedule_print_open'); } catch (error) { showError(exportError, 'Printing is unavailable here. Use your browser\'s Print command or export CSV.'); }
    });
    exportButton.addEventListener('click', function () {
      if (!validateForExport()) return;
      var url;
      var anchor;
      try {
        var csv = makeCSV(business.value.trim(), date.value, state.tasks);
        url = win.URL.createObjectURL(new win.Blob([csv], { type: 'text/csv;charset=utf-8;' }));
        anchor = element('a', { href: url, download: 'kitchen-cleaning-schedule-' + date.value + '.csv' });
        doc.body.appendChild(anchor);
        anchor.click();
        track('cleaning_schedule_csv_export');
        announce('Your CSV is ready to save. Open it in your spreadsheet app.');
      } catch (error) { showError(exportError, 'The CSV could not be prepared in this browser. Try Print or save PDF.'); }
      finally {
        if (anchor) anchor.remove();
        if (url) win.setTimeout(function () { win.URL.revokeObjectURL(url); }, 1000);
      }
    });

    // Share the public tool URL only. Never include entered kitchen or task data.
    var copyToolButton = doc.getElementById('copy-tool-link');
    var shareStatus = doc.getElementById('share-tool-status');
    var shareFallback = doc.getElementById('share-tool-fallback');
    var shareInput = doc.getElementById('share-tool-url');
    var publicToolLink = 'https://blueroll.app/kitchen-cleaning-schedule-generator.html?utm_source=customer_share&utm_medium=referral&utm_campaign=cleaning_schedule_shared';
    function trackSharing(name, channel) {
      try { if (typeof win.gtag === 'function') win.gtag('event', name, { channel: channel, tool: 'cleaning_schedule' }); } catch (error) {}
    }
    if (copyToolButton && shareStatus && shareFallback && shareInput) {
      shareInput.value = publicToolLink;
      copyToolButton.disabled = false;
      copyToolButton.addEventListener('click', function () {
        function selectShareLink() {
          shareFallback.hidden = false;
          shareInput.focus();
          shareInput.select();
          shareStatus.textContent = 'Tool link selected. Press Ctrl+C or Command+C to copy, then paste it where you want to share.';
          trackSharing('cleaning_schedule_link_copy_fallback', 'customer_share');
        }
        try {
          if (!win.navigator.clipboard || typeof win.navigator.clipboard.writeText !== 'function') { selectShareLink(); return; }
          win.navigator.clipboard.writeText(publicToolLink).then(function () {
            shareFallback.hidden = true;
            shareStatus.textContent = 'Tool link copied. Your kitchen name and schedule were not included.';
            trackSharing('cleaning_schedule_link_copy', 'customer_share');
          }).catch(selectShareLink);
        } catch (error) { selectShareLink(); }
      });
      shareInput.addEventListener('click', function () { shareInput.select(); });
    }
    ['whatsapp', 'linkedin'].forEach(function (channel) {
      var link = doc.getElementById('share-tool-' + channel);
      if (link) link.addEventListener('click', function () { trackSharing('cleaning_schedule_share_open', channel); });
    });

    date.value = currentMonday(new Date());
    renderEditor();
    renderPreview();
    generator.hidden = false;
    printButton.disabled = false;
    exportButton.disabled = false;
    win.addEventListener('beforeprint', renderPreview);
  }

  return { createDefaultTasks: createDefaultTasks, parseISODate: parseISODate, currentMonday: currentMonday, weekDates: weekDates, validateTasks: validateTasks, csvCell: csvCell, makeCSV: makeCSV, init: init };
});
