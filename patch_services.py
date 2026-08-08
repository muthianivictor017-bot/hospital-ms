import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Fix async syntax
c = c.replace('async async function', 'async function')

# 2. Add services to dataCache
c = c.replace(
    "let dataCache = {\n  patients:[], admissions:[], appointments:[], doctors:[], prescriptions:[], billing:[], inventory:[], wards:[], users:[], labs:[], shaClaims:[], departments:[], departmentAssignments:[]\n};",
    "let dataCache = {\n  patients:[], admissions:[], appointments:[], doctors:[], prescriptions:[], billing:[], inventory:[], wards:[], users:[], labs:[], shaClaims:[], departments:[], departmentAssignments:[], services:[]\n};"
)

# 3. Add services to collection arrays
c = c.replace(
    "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments'];",
    "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments','services'];"
)
parts = c.split("const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments'];")
if len(parts) == 3:
    c = parts[0] + "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments','services'];" + parts[1] + "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments','services'];" + parts[2]

c = c.replace(
    "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','users','labs','shaClaims','departments','departmentAssignments'];",
    "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','users','labs','shaClaims','departments','departmentAssignments','services'];"
)
c = c.replace(
    "['dashboard','patients','admissions','appointments','wards','doctors','prescriptions','billing','labs','inventory','users','sha','departments'].forEach(refreshPageData);",
    "['dashboard','patients','admissions','appointments','wards','doctors','prescriptions','billing','labs','inventory','users','sha','departments','services'].forEach(refreshPageData);"
)
parts2 = c.split("const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments'];")
if len(parts2) == 3:
    c = parts2[0] + "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments','services'];" + parts2[1] + "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','wards','labs','shaClaims','departments','departmentAssignments','services'];" + parts2[2]

# 4. Nav item
c = c.replace(
    '<div class="nav-item" data-page="inventory"><i class="fas fa-pills"></i><span>Inventory</span></div>\n<div class="nav-item" data-page="messaging">',
    '<div class="nav-item" data-page="inventory"><i class="fas fa-pills"></i><span>Inventory</span></div>\n<div class="nav-item" data-page="services"><i class="fas fa-list-alt"></i><span>Services</span><span class="badge" id="servicesBadge">0</span></div>\n<div class="nav-item" data-page="messaging">'
)

# 5. Page section
services_page = '''<!-- SERVICES PAGE -->
<div class="page-section" id="page-services">
<div class="search-bar"><input type="text" id="servicesSearch" placeholder="Search services..." onkeyup="searchServices()"><select id="servicesCategoryFilter" onchange="filterServices()"><option value="">All Categories</option><option value="Consultation">Consultation</option><option value="Laboratory">Laboratory</option><option value="Radiology">Radiology</option><option value="Surgery">Surgery</option><option value="Pharmacy">Pharmacy</option><option value="Nursing">Nursing</option><option value="Room & Board">Room & Board</option><option value="Emergency">Emergency</option><option value="Procedure">Procedure</option><option value="Other">Other</option></select><button class="btn-sm btn-primary" onclick="openModal('service')"><i class="fas fa-plus"></i> Add Service</button></div>
<div class="card"><div class="card-header"><h3><i class="fas fa-list-alt"></i> Medical Services & Pricing</h3></div>
<div class="card-body"><table class="data-table"><thead><tr><th>Service Code</th><th>Service Name</th><th>Category</th><th>Cost (KSh)</th><th>Status</th><th>Actions</th></tr></thead><tbody id="servicesTable"></tbody></table></div>
</div>
</div>

'''
c = c.replace('<!-- USERS PAGE -->', services_page + '<!-- USERS PAGE -->')

# 6. navigateTo
c = c.replace(
    "else if(page === 'inventory'){ btn.innerHTML = '<i class=\"fas fa-plus\"></i> Add Item'; btn.onclick = () => openModal('inventory'); btn.style.display = ''; }\n    else if(page === 'users'){",
    "else if(page === 'inventory'){ btn.innerHTML = '<i class=\"fas fa-plus\"></i> Add Item'; btn.onclick = () => openModal('inventory'); btn.style.display = ''; }\n    else if(page === 'services'){ btn.innerHTML = '<i class=\"fas fa-plus\"></i> Add Service'; btn.onclick = () => openModal('service'); btn.style.display = ''; }\n    else if(page === 'users'){"
)
c = c.replace(
    "if(page === 'settings'){",
    "if(page === 'services'){ renderServices(); }\n    if(page === 'settings'){"
)

# 7. updateStats
c = c.replace(
    "const statDeptEl = document.getElementById('statDepartments');\n    if(statDeptEl) statDeptEl.textContent = dataCache.departments.length;\n}",
    "const statDeptEl = document.getElementById('statDepartments');\n    if(statDeptEl) statDeptEl.textContent = dataCache.departments.length;\n    const servicesBadge = document.getElementById('servicesBadge');\n    if(servicesBadge) servicesBadge.textContent = dataCache.services.length;\n}"
)

# 8. refreshPageData
c = c.replace(
    "case 'departments': renderDepartments(); renderDepartmentQueue(); break;\n    }",
    "case 'departments': renderDepartments(); renderDepartmentQueue(); break;\n        case 'services': renderServices(); break;\n    }"
)

# 9. renderServices functions
svc_funcs = '''
// ==================== SERVICES MODULE ====================
function renderServices(){
    const tbody = document.getElementById('servicesTable');
    const catFilter = document.getElementById('servicesCategoryFilter').value;
    let services = dataCache.services;
    if(catFilter) services = services.filter(s => s.category === catFilter);
    if(services.length === 0){ tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><i class="fas fa-list-alt"></i><p>No services found. Add your first service.</p></td></tr>'; return; }
    tbody.innerHTML = services.sort((a,b) => (a.name || '').localeCompare(b.name || '')).map(s => {
        const statusClass = s.status === 'Active' ? 'active' : 'cancelled';
        return `<tr><td><strong>${s.serviceCode || s.id.slice(-4)}</strong></td><td>${s.name}</td><td>${s.category || '-'}</td><td style="font-weight:600;color:var(--primary)">KSh ${parseFloat(s.cost || 0).toFixed(2)}</td><td><span class="status-badge status-${statusClass}">${s.status || 'Active'}</span></td><td><button class="btn-sm btn-warning" onclick="editService('${s.id}')"><i class="fas fa-edit"></i></button> <button class="btn-sm btn-danger" onclick="deleteService('${s.id}')"><i class="fas fa-trash"></i></button></td></tr>`;
    }).join('');
}
function searchServices(){ const q=document.getElementById('servicesSearch').value.toLowerCase(); document.querySelectorAll('#servicesTable tr').forEach(r => r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none'); }
function filterServices(){ renderServices(); }
async function deleteService(id){ if(!confirm('Delete this service? It will no longer be available for billing.'))return; await deleteData('services',id); renderServices(); updateStats(); toast('Service deleted', 'info'); }
function editService(id){ openModal('service',id); }

'''
c = c.replace("// ==================== SEARCH FUNCTIONS ====================", svc_funcs + "// ==================== SEARCH FUNCTIONS ====================")

# 10. Service modal in openModal
svc_modal = '''        case 'service':
            title.textContent = isEdit ? 'Edit Service' : 'Add Service';
            body.innerHTML = `
                <div class="form-row"><div class="form-group"><label>Service Name *</label><input type="text" id="m_svc_name" value="${item.name || ''}" placeholder="e.g., General Consultation" required></div><div class="form-group"><label>Service Code</label><input type="text" id="m_svc_code" value="${item.serviceCode || ''}" placeholder="e.g., SRV-001"></div></div>
                <div class="form-row"><div class="form-group"><label>Category *</label><select id="m_svc_category" required><option value="">Select</option><option value="Consultation" ${item.category === 'Consultation' ? 'selected' : ''}>Consultation</option><option value="Laboratory" ${item.category === 'Laboratory' ? 'selected' : ''}>Laboratory</option><option value="Radiology" ${item.category === 'Radiology' ? 'selected' : ''}>Radiology</option><option value="Surgery" ${item.category === 'Surgery' ? 'selected' : ''}>Surgery</option><option value="Pharmacy" ${item.category === 'Pharmacy' ? 'selected' : ''}>Pharmacy</option><option value="Nursing" ${item.category === 'Nursing' ? 'selected' : ''}>Nursing</option><option value="Room & Board" ${item.category === 'Room & Board' ? 'selected' : ''}>Room & Board</option><option value="Emergency" ${item.category === 'Emergency' ? 'selected' : ''}>Emergency</option><option value="Procedure" ${item.category === 'Procedure' ? 'selected' : ''}>Procedure</option><option value="Other" ${item.category === 'Other' ? 'selected' : ''}>Other</option></select></div><div class="form-group"><label>Cost (KSh) *</label><input type="number" step="0.01" id="m_svc_cost" value="${item.cost || ''}" placeholder="e.g., 1500" required></div></div>
                <div class="form-group"><label>Description</label><textarea id="m_svc_desc" placeholder="Brief description of the service">${item.description || ''}</textarea></div>
                <div class="form-group"><label>Status</label><select id="m_svc_status"><option value="Active" ${(item.status || 'Active') === 'Active' ? 'selected' : ''}>Active</option><option value="Inactive" ${item.status === 'Inactive' ? 'selected' : ''}>Inactive</option></select></div>
            `;
            break;
'''
c = c.replace("        case 'department':\n            title.textContent = isEdit ? 'Edit Department' : 'Add Department';", svc_modal + "        case 'department':\n            title.textContent = isEdit ? 'Edit Department' : 'Add Department';")

# 11. Service save in saveModal
svc_save = '''        case 'service':
            data = {id:currentEditId, name:document.getElementById('m_svc_name').value.trim(), serviceCode:document.getElementById('m_svc_code').value.trim(), category:document.getElementById('m_svc_category').value, cost:parseFloat(document.getElementById('m_svc_cost').value) || 0, description:document.getElementById('m_svc_desc').value, status:document.getElementById('m_svc_status').value};
            break;
'''
c = c.replace("    try {\n        if(currentModalType === 'user'){", svc_save + "    try {\n        if(currentModalType === 'user'){")

# 12. Replace billing modal
old_billing = c[c.find("case 'billing':\n            title.textContent = isEdit ? 'Edit Invoice' : 'New Invoice';"):c.find("            if(isEdit && item.patientId) setTimeout(() => updateInsuranceInfo(), 100);\n            break;", c.find("case 'billing':\n            title.textContent = isEdit ? 'Edit Invoice' : 'New Invoice';"))+len("            if(isEdit && item.patientId) setTimeout(() => updateInsuranceInfo(), 100);\n            break;")]
new_billing = """case 'billing':
            title.textContent = isEdit ? 'Edit Invoice' : 'New Invoice';
            const patientOptions = dataCache.patients.map(p => `<option value="${p.id}" ${item.patientId === p.id ? 'selected' : ''}>${p.name}</option>`).join('');
            const activeServices = dataCache.services.filter(s => s.status === 'Active').sort((a,b) => (a.category||'').localeCompare(b.category||'') || (a.name||'').localeCompare(b.name||''));
            let currentSvcIds = [];
            if(isEdit && item.services && item.services.length > 0){
                currentSvcIds = item.services.map(s => {
                    if(typeof s === 'object' && s.id) return s.id;
                    const found = dataCache.services.find(x => x.name === s);
                    return found ? found.id : '';
                }).filter(id => id);
            }
            let servicesHtml = '';
            if(activeServices.length === 0){
                servicesHtml = '<div style="padding:12px;color:var(--gray);font-size:13px"><i class="fas fa-info-circle"></i> No active services in catalog. <a href="#" onclick="closeModal();navigateTo(\'services\');" style="color:var(--primary)">Add services first</a>.</div>';
            } else {
                let lastCat = '';
                activeServices.forEach(svc => {
                    if(svc.category !== lastCat){ servicesHtml += `<div style="font-size:11px;font-weight:600;color:var(--gray);text-transform:uppercase;margin:8px 0 4px;padding-top:6px;border-top:1px solid var(--border)">${svc.category || 'General'}</div>`; lastCat = svc.category; }
                    const isChecked = currentSvcIds.includes(svc.id) ? 'checked' : '';
                    servicesHtml += `<label style="display:flex;align-items:center;gap:8px;padding:6px 8px;cursor:pointer;border-radius:6px;transition:background 0.15s" onmouseover="this.style.background='var(--light)'" onmouseout="this.style.background='transparent'"><input type="checkbox" class="bill-service-check" value="${svc.id}" data-cost="${svc.cost || 0}" onchange="updateBillTotal()" ${isChecked} style="width:16px;height:16px;accent-color:var(--primary)"><span style="flex:1;font-size:13px">${svc.name}</span><span style="font-weight:600;color:var(--primary);font-size:13px">KSh ${parseFloat(svc.cost || 0).toFixed(2)}</span></label>`;
                });
            }
            body.innerHTML = `
                <div class="form-row"><div class="form-group"><label>Patient *</label><select id="m_bill_patient" onchange="updateInsuranceInfo()" required><option value="">Select</option>${patientOptions}</select></div><div class="form-group"><label>Date *</label><input type="date" id="m_bill_date" value="${item.date || new Date().toISOString().split('T')[0]}" required></div></div>
                <div id="insuranceInfoBox" style="display:none;margin-bottom:16px;padding:12px;background:#eff6ff;border-radius:8px;font-size:12px;color:#1e40af"></div>
                <div class="form-group"><label>Select Services *</label>
                <div id="billServicesList" style="max-height:220px;overflow-y:auto;border:2px solid var(--border);border-radius:10px;padding:10px;background:white">${servicesHtml}</div>
                <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center"><span style="font-size:12px;color:var(--gray)">Check services to auto-calculate total</span><span style="font-size:14px;font-weight:600">Auto Total: <span id="billAutoTotal" style="color:var(--primary);font-size:18px">KSh 0.00</span></span></div>
                </div>
                <div class="form-row"><div class="form-group"><label>Total Amount (KSh) * <span style="color:var(--gray);font-size:11px">(Editable override)</span></label><input type="number" step="0.01" id="m_bill_amount" value="${item.amount || ''}" onfocus="this.dataset.userEdited='true'" required></div><div class="form-group"><label>Insurance Coverage (KSh)</label><input type="number" step="0.01" id="m_bill_insurance" value="${item.insuranceAmount || '0'}" placeholder="Amount covered by insurance"></div></div>
                <div class="form-row"><div class="form-group"><label><i class="fas fa-shield-heart" style="color:#1e40af"></i> SHA Claim</label><select id="m_bill_sha_claim"><option value="">No SHA Claim</option><option value="Draft" ${item.shaClaimStatus === 'Draft' ? 'selected' : ''}>Create Draft Claim</option><option value="Submitted" ${item.shaClaimStatus === 'Submitted' ? 'selected' : ''}>Submit to SHA</option></select></div><div class="form-group"><label>SHA Claim Amount (KSh)</label><input type="number" step="0.01" id="m_bill_sha_amount" value="${item.shaClaimAmount || ''}" placeholder="Amount to claim from SHA"></div></div>
                <div class="form-row"><div class="form-group"><label>Status</label><select id="m_bill_status"><option value="Pending" ${(item.status || 'Pending') === 'Pending' ? 'selected' : ''}>Pending</option><option value="Insurance Pending" ${item.status === 'Insurance Pending' ? 'selected' : ''}>Insurance Pending</option><option value="Paid" ${item.status === 'Paid' ? 'selected' : ''}>Paid</option><option value="Cancelled" ${item.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option></select></div><div class="form-group"><label>Due Date</label><input type="date" id="m_bill_due_date" value="${item.dueDate || ''}"></div></div>
                <div class="form-group"><label>Notes</label><textarea id="m_bill_notes" placeholder="Additional notes...">${item.notes || ''}</textarea></div>`;
            if(isEdit && item.patientId) setTimeout(() => updateInsuranceInfo(), 100);
            setTimeout(() => updateBillTotal(), 50);
            break;"""
c = c.replace(old_billing, new_billing)

# 13. Add updateBillTotal
bill_help = '''// ==================== BILLING SERVICE HELPERS ====================
function updateBillTotal(){
    let total = 0;
    const selected = [];
    document.querySelectorAll('.bill-service-check:checked').forEach(cb => {
        const cost = parseFloat(cb.dataset.cost) || 0;
        total += cost;
        const svc = dataCache.services.find(s => s.id === cb.value);
        if(svc) selected.push(svc.name);
    });
    const autoTotalEl = document.getElementById('billAutoTotal');
    if(autoTotalEl) autoTotalEl.textContent = 'KSh ' + total.toFixed(2);
    const amountInput = document.getElementById('m_bill_amount');
    if(amountInput && !amountInput.dataset.userEdited){
        amountInput.value = total.toFixed(2);
    }
}

'''
c = c.replace("// ==================== PAYMENT MODAL ====================", bill_help + "// ==================== PAYMENT MODAL ====================")

# 14. Replace saveModal billing case
old_save = c[c.find("        case 'billing':\n            const billPatientId = document.getElementById('m_bill_patient').value;"):c.find("            break;\n        case 'lab':", c.find("        case 'billing':\n            const billPatientId = document.getElementById('m_bill_patient').value;"))]
new_save = """        case 'billing':
            const billPatientId = document.getElementById('m_bill_patient').value;
            const selectedServices = [];
            document.querySelectorAll('.bill-service-check:checked').forEach(cb => {
                const svc = dataCache.services.find(s => s.id === cb.value);
                if(svc) selectedServices.push({id: svc.id, name: svc.name, cost: parseFloat(svc.cost) || 0});
            });
            const autoTotal = selectedServices.reduce((sum, s) => sum + s.cost, 0);
            const manualTotal = parseFloat(document.getElementById('m_bill_amount').value) || 0;
            const billAmount = manualTotal > 0 ? manualTotal : autoTotal;
            const billInsurance = parseFloat(document.getElementById('m_bill_insurance').value) || 0;
            const billStatus = document.getElementById('m_bill_status').value;
            const shaClaimStatus = document.getElementById('m_bill_sha_claim')?.value || '';
            const shaClaimAmount = parseFloat(document.getElementById('m_bill_sha_amount')?.value) || 0;
            data = {id:currentEditId, patientId:billPatientId, date:document.getElementById('m_bill_date').value, services:selectedServices, amount:billAmount, insuranceAmount:billInsurance, status:billStatus, dueDate:document.getElementById('m_bill_due_date').value, notes:document.getElementById('m_bill_notes').value, invoiceNumber: currentEditId ? (dataCache.billing.find(b => b.id === currentEditId) || {}).invoiceNumber : 'INV-' + Date.now().toString().slice(-6), shaClaimStatus, shaClaimAmount};
            if(shaClaimStatus && shaClaimAmount > 0){
                const shaPatient = dataCache.patients.find(p => p.id === billPatientId);
                if(shaPatient && shaPatient.shaNumber){
                    const shaClaim = {
                        patientId: billPatientId,
                        shaNumber: shaPatient.shaNumber,
                        date: document.getElementById('m_bill_date').value,
                        claimNumber: 'SHA-' + Date.now().toString().slice(-6),
                        services: selectedServices.map(s => s.name),
                        amount: shaClaimAmount,
                        coPay: billAmount - shaClaimAmount - billInsurance,
                        status: shaClaimStatus,
                        diagnosis: '',
                        notes: 'Auto-generated from invoice ' + (currentEditId ? (dataCache.billing.find(b => b.id === currentEditId) || {}).invoiceNumber : 'new'),
                        submittedBy: currentUser ? (currentUser.displayName || currentUser.email) : 'System',
                        submittedAt: new Date().toISOString()
                    };
                    saveData('shaClaims', shaClaim);
                    toast('SHA claim created: ' + shaClaim.claimNumber, 'success');
                }
            }
            break;
"""
c = c.replace(old_save, new_save)

# 15-17. Update viewInvoiceDetail, printInvoice, printReceipt
old_view = '''            <table class="services-table">
                <thead><tr><th>Service</th><th style="text-align:right">Amount</th></tr></thead>
                <tbody>
                    ${(invoice.services || []).map(s => `<tr><td>${s}</td><td style="text-align:right">-</td></tr>`).join('')}
                    <tr><td><strong>Total</strong></td><td style="text-align:right"><strong>KSh ${total.toFixed(2)}</strong></td></tr>
                </tbody>
            </table>'''
new_view = '''            <table class="services-table">
                <thead><tr><th>Service</th><th style="text-align:right">Qty</th><th style="text-align:right">Unit Cost</th><th style="text-align:right">Amount</th></tr></thead>
                <tbody>
                    ${(invoice.services || []).map(s => {
                        const isObj = typeof s === 'object';
                        const name = isObj ? s.name : s;
                        const cost = isObj ? (parseFloat(s.cost) || 0) : 0;
                        return `<tr><td>${name}</td><td style="text-align:right">1</td><td style="text-align:right">KSh ${cost.toFixed(2)}</td><td style="text-align:right">KSh ${cost.toFixed(2)}</td></tr>`;
                    }).join('')}
                    <tr><td colspan="3"><strong>Subtotal</strong></td><td style="text-align:right"><strong>KSh ${total.toFixed(2)}</strong></td></tr>
                </tbody>
            </table>'''
c = c.replace(old_view, new_view)

old_print_inv = """    document.getElementById('printInvoiceServices').innerHTML = (invoice.services || []).map((s, i) => {
        const avg = total / (invoice.services || []).length;
        return `<tr><td>${s}</td><td style="text-align:right">1</td><td style="text-align:right">KSh ${avg.toFixed(2)}</td><td style="text-align:right">KSh ${avg.toFixed(2)}</td></tr>`;
    }).join('');"""
new_print_inv = """    document.getElementById('printInvoiceServices').innerHTML = (invoice.services || []).map(s => {
        const isObj = typeof s === 'object';
        const name = isObj ? s.name : s;
        const cost = isObj ? (parseFloat(s.cost) || 0) : 0;
        return `<tr><td>${name}</td><td style="text-align:right">1</td><td style="text-align:right">KSh ${cost.toFixed(2)}</td><td style="text-align:right">KSh ${cost.toFixed(2)}</td></tr>`;
    }).join('');"""
c = c.replace(old_print_inv, new_print_inv)

old_print_rec = """    document.getElementById('receiptServices').innerHTML = (invoice.services || []).map((s, i) => {
        const avg = total / (invoice.services || []).length;
        return `<tr><td>${s}</td><td style="text-align:right">1</td><td style="text-align:right">KSh ${avg.toFixed(2)}</td><td style="text-align:right">KSh ${avg.toFixed(2)}</td></tr>`;
    }).join('');"""
new_print_rec = """    document.getElementById('receiptServices').innerHTML = (invoice.services || []).map(s => {
        const isObj = typeof s === 'object';
        const name = isObj ? s.name : s;
        const cost = isObj ? (parseFloat(s.cost) || 0) : 0;
        return `<tr><td>${name}</td><td style="text-align:right">1</td><td style="text-align:right">KSh ${cost.toFixed(2)}</td><td style="text-align:right">KSh ${cost.toFixed(2)}</td></tr>`;
    }).join('');"""
c = c.replace(old_print_rec, new_print_rec)

# 18. CSV exports
c = c.replace('"${(b.services||[]).join(\'; \')}"', '"${(b.services||[]).map(s => typeof s === \'object\' ? s.name : s).join(\'; \')}"')

# 19. Demo services
demo_idx = c.find("// DEMO USERS")
demo_services = '''    // DEMO SERVICES
    const demoServices = [
        {id:'svc1',hospitalId:'DEMO',name:'General Consultation',serviceCode:'CONS-001',category:'Consultation',cost:1500,description:'Standard doctor consultation',status:'Active'},
        {id:'svc2',hospitalId:'DEMO',name:'Specialist Consultation',serviceCode:'CONS-002',category:'Consultation',cost:3000,description:'Specialist doctor consultation',status:'Active'},
        {id:'svc3',hospitalId:'DEMO',name:'ECG / Electrocardiogram',serviceCode:'LAB-001',category:'Laboratory',cost:1200,description:'Heart rhythm test',status:'Active'},
        {id:'svc4',hospitalId:'DEMO',name:'Blood Work (Full Panel)',serviceCode:'LAB-002',category:'Laboratory',cost:2500,description:'CBC, CMP, lipid profile',status:'Active'},
        {id:'svc5',hospitalId:'DEMO',name:'X-Ray (Chest)',serviceCode:'RAD-001',category:'Radiology',cost:1800,description:'Chest X-ray imaging',status:'Active'},
        {id:'svc6',hospitalId:'DEMO',name:'MRI Scan',serviceCode:'RAD-002',category:'Radiology',cost:15000,description:'Magnetic resonance imaging',status:'Active'},
        {id:'svc7',hospitalId:'DEMO',name:'CT Scan',serviceCode:'RAD-003',category:'Radiology',cost:8000,description:'Computed tomography scan',status:'Active'},
        {id:'svc8',hospitalId:'DEMO',name:'Ultrasound',serviceCode:'RAD-004',category:'Radiology',cost:3500,description:'General ultrasound imaging',status:'Active'},
        {id:'svc9',hospitalId:'DEMO',name:'Minor Surgery',serviceCode:'SURG-001',category:'Surgery',cost:25000,description:'Day-case minor surgical procedure',status:'Active'},
        {id:'svc10',hospitalId:'DEMO',name:'Wound Dressing',serviceCode:'PROC-001',category:'Procedure',cost:500,description:'Professional wound dressing change',status:'Active'},
        {id:'svc11',hospitalId:'DEMO',name:'Nebulization',serviceCode:'PROC-002',category:'Procedure',cost:800,description:'Respiratory nebulizer therapy',status:'Active'},
        {id:'svc12',hospitalId:'DEMO',name:'Oxygen Therapy (per hour)',serviceCode:'PROC-003',category:'Procedure',cost:600,description:'Supplemental oxygen administration',status:'Active'},
        {id:'svc13',hospitalId:'DEMO',name:'General Ward (per day)',serviceCode:'ROOM-001',category:'Room & Board',cost:3500,description:'General ward bed per day',status:'Active'},
        {id:'svc14',hospitalId:'DEMO',name:'ICU (per day)',serviceCode:'ROOM-002',category:'Room & Board',cost:12000,description:'Intensive care unit per day',status:'Active'},
        {id:'svc15',hospitalId:'DEMO',name:'Emergency Stabilization',serviceCode:'EMR-001',category:'Emergency',cost:5000,description:'Emergency room stabilization fee',status:'Active'},
        {id:'svc16',hospitalId:'DEMO',name:'Ambulance Service',serviceCode:'EMR-002',category:'Emergency',cost:8000,description:'Emergency ambulance transport',status:'Active'},
        {id:'svc17',hospitalId:'DEMO',name:'COVID-19 Test',serviceCode:'LAB-003',category:'Laboratory',cost:2500,description:'PCR COVID-19 test',status:'Active'},
        {id:'svc18',hospitalId:'DEMO',name:'Physiotherapy Session',serviceCode:'PROC-004',category:'Procedure',cost:2000,description:'Physical therapy session',status:'Active'},
        {id:'svc19',hospitalId:'DEMO',name:'Vaccination',serviceCode:'PHARM-001',category:'Pharmacy',cost:800,description:'Standard vaccination administration',status:'Active'},
        {id:'svc20',hospitalId:'DEMO',name:'Dental Extraction',serviceCode:'SURG-002',category:'Surgery',cost:4500,description:'Tooth extraction procedure',status:'Active'}
    ];
    if(secureGet(getStorageKey('services', 'DEMO'), []).length === 0){
        secureSet(getStorageKey('services', 'DEMO'), demoServices);
    }

'''
c = c[:demo_idx] + demo_services + c[demo_idx:]

# 20. seedNewHospitalData
c = c.replace(
    "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','labs','users'];",
    "const cols = ['patients','admissions','appointments','doctors','prescriptions','billing','inventory','labs','users','services'];"
)

with open('index_patched.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done! Saved as index_patched.html")
print(f"Output size: {len(c)} characters")
