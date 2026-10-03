import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update initial dashboard recovery rate & slot quota text in HTML
content = re.sub(r'<span id="dashRecoveryRate"[^>]*>[\s\S]*?</span>', '<span id="dashRecoveryRate" class="text-base font-extrabold text-white num-tabular">0%</span>', content)
content = re.sub(r'<p id="dashSlotQuotaText"[^>]*>[\s\S]*?</p>', '<p id="dashSlotQuotaText" class="text-[11px] text-success font-medium">0 / 250 Slots Used</p>', content)
content = re.sub(r'<span id="slotsRemainingHeader"[^>]*>[\s\S]*?</span>', '<span id="slotsRemainingHeader" class="text-xs font-bold text-success bg-success/10 px-2.5 py-1 rounded-full border border-success/30 num-tabular">0 / 250 slots</span>', content)

# 2. Update renderDevicesGrid empty state
old_dev_empty = '''      if (!list || list.length === 0) {
        container.innerHTML = `
          <div class="col-span-full glass-card p-10 rounded-2xl text-center border border-borderDark">
            <i data-lucide="smartphone" class="w-10 h-10 text-success/40 mx-auto mb-2"></i>
            <h4 class="text-sm font-bold text-white">No Enrolled Devices</h4>
            <p class="text-xs text-textSec mt-1">Enroll a smartphone using Knox QR Code or click "+ Add Device".</p>
            <button type="button" onclick="openAddDeviceModal()" class="mt-4 px-4 py-2 rounded-xl bg-brand text-white text-xs font-bold shadow">
              + Add First Device
            </button>
          </div>
        `;
        lucide.createIcons();
        return;
      }'''

new_dev_empty = '''      if (!list || list.length === 0) {
        container.innerHTML = `
          <div class="col-span-full glass-card p-12 rounded-2xl text-center border border-borderDark">
            <i data-lucide="smartphone" class="w-12 h-12 text-success/40 mx-auto mb-3"></i>
            <h4 class="text-sm font-bold text-white">No devices yet</h4>
            <p class="text-xs text-textSec mt-1">Tap + Add Device to start.</p>
            <button type="button" onclick="openAddDeviceModal()" class="mt-4 px-4 py-2 rounded-xl bg-gradient-to-r from-brand to-brandEnd text-white text-xs font-bold shadow">
              + Add Device
            </button>
          </div>
        `;
        lucide.createIcons();
        return;
      }'''

if old_dev_empty in content:
    content = content.replace(old_dev_empty, new_dev_empty)
else:
    # Try regex replacement for dev empty state
    content = re.sub(
        r'function renderDevicesGrid\(list = appState\.devices\) \{\s*const container = document\.getElementById\(\'devicesGrid\'\);\s*if \(!list \|\| list\.length === 0\) \{[\s\S]*?return;\s*\}',
        'function renderDevicesGrid(list = appState.devices) {\n      const container = document.getElementById(\'devicesGrid\');\n' + new_dev_empty,
        content
    )

# 3. Update renderCustomersGrid empty state
new_cust_empty = '''      if (!list || list.length === 0) {
        container.innerHTML = `
          <div class="col-span-full glass-card p-12 rounded-2xl text-center border border-borderDark">
            <i data-lucide="users" class="w-12 h-12 text-brand/40 mx-auto mb-3"></i>
            <h4 class="text-sm font-bold text-white">No customers yet</h4>
            <p class="text-xs text-textSec mt-1">Tap + Add Customer.</p>
            <button type="button" onclick="openAddCustomerModal()" class="mt-4 px-4 py-2 rounded-xl bg-gradient-to-r from-brand to-brandEnd text-white text-xs font-bold shadow">
              + Add Customer
            </button>
          </div>
        `;
        lucide.createIcons();
        return;
      }'''

content = re.sub(
    r'function renderCustomersGrid\(list = appState\.customers\) \{\s*const container = document\.getElementById\(\'customersGrid\'\);\s*if \(!list \|\| list\.length === 0\) \{[\s\S]*?return;\s*\}',
    'function renderCustomersGrid(list = appState.customers) {\n      const container = document.getElementById(\'customersGrid\');\n' + new_cust_empty,
    content
)

# 4. Update renderPaymentsTable empty state
content = re.sub(
    r'if \(!list \|\| list\.length === 0\) \{\s*tbody\.innerHTML = `<tr><td colspan="6" class="[^"]*">[^<]*</td></tr>`;\s*return;\s*\}',
    'if (!list || list.length === 0) {\n        tbody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-textSec text-xs">No payments recorded yet.</td></tr>`;\n        return;\n      }',
    content
)

# 5. Update renderRecentPayments empty state
content = re.sub(
    r'function renderRecentPayments\(\) \{\s*const container = document\.getElementById\(\'dashRecentPayments\'\);\s*const list = appState\.payments\.slice\(0, 3\);\s*if \(!list \|\| list\.length === 0\) \{[\s\S]*?return;\s*\}',
    'function renderRecentPayments() {\n      const container = document.getElementById(\'dashRecentPayments\');\n      const list = appState.payments.slice(0, 3);\n      if (!list || list.length === 0) {\n        container.innerHTML = `<p class="text-xs text-textSec text-center py-6">No payments recorded yet.</p>`;\n        return;\n      }',
    content
)

# 6. Update updateDashboardCounters & renderDashboardChart
counters_replacement = '''    function updateDashboardCounters() {
      const totalCust = appState.customers.length;
      const totalDev = appState.devices.length;
      const maxSlots = Number(appState.currentBusiness?.device_limit) || 250;
      const availSlots = Math.max(0, maxSlots - totalDev);
      
      // Calculate today's collection from real payments only (no fallback)
      const today = new Date().toDateString();
      const todaySum = appState.payments
        .filter(p => {
          const d = p.created_at || p.payment_date;
          return d && new Date(d).toDateString() === today;
        })
        .reduce((sum, p) => sum + (Number(p.amount) || 0), 0);

      // Real Recovery Rate based on active vs locked devices
      const activeDev = appState.devices.filter(d => !d.is_locked).length;
      const recoveryPct = totalDev > 0 ? Math.round((activeDev / totalDev) * 100) : 0;
      
      const recRateEl = document.getElementById('dashRecoveryRate');
      if (recRateEl) recRateEl.innerText = `${recoveryPct}%`;

      const circle = document.getElementById('dashRecoveryCircle');
      if (circle) {
        const offset = 201 - (201 * (recoveryPct / 100));
        circle.style.strokeDashoffset = offset;
      }

      // Run count-up animations with real numbers
      animateCounter(document.getElementById('statCustomers'), totalCust);
      animateCounter(document.getElementById('statDevices'), totalDev);
      animateCounter(document.getElementById('statSlots'), availSlots);
      animateCounter(document.getElementById('statToday'), todaySum, true, "PKR ");

      // Update badges: Show real count / real limit
      const custBadge = document.getElementById('customersCountBadge');
      if (custBadge) custBadge.innerText = `${totalCust} Total`;

      const devBadge = document.getElementById('devicesCountBadge');
      if (devBadge) devBadge.innerText = `${totalDev} Devices`;

      const slotHead = document.getElementById('slotsRemainingHeader');
      if (slotHead) slotHead.innerText = `${totalDev} / ${maxSlots} slots`;

      const slotText = document.getElementById('dashSlotQuotaText');
      if (slotText) slotText.innerText = `${totalDev} / ${maxSlots} slots used (${availSlots} available)`;

      // Update Channel Summaries on Payments screen
      let jazz = 0, easy = 0, raast = 0, cash = 0;
      appState.payments.forEach(p => {
        const amt = Number(p.amount) || 0;
        const ch = (p.channel || p.payment_method || '').toLowerCase();
        if (ch.includes('jazz')) jazz += amt;
        else if (ch.includes('easy')) easy += amt;
        else if (ch.includes('raast')) raast += amt;
        else cash += amt;
      });

      const pJazz = document.getElementById('payChanJazz');
      if (pJazz) pJazz.innerText = `PKR ${jazz.toLocaleString()}`;
      const pEasy = document.getElementById('payChanEasy');
      if (pEasy) pEasy.innerText = `PKR ${easy.toLocaleString()}`;
      const pRaast = document.getElementById('payChanRaast');
      if (pRaast) pRaast.innerText = `PKR ${raast.toLocaleString()}`;
      const pCash = document.getElementById('payChanCash');
      if (pCash) pCash.innerText = `PKR ${cash.toLocaleString()}`;

      // Refresh chart with real payments data
      renderDashboardChart();
    }

    // --------------------------------------------------------
    // 9. CHART.JS: MONTHLY COLLECTIONS (REAL PAYMENTS AGGREGATION)
    // --------------------------------------------------------
    function renderDashboardChart() {
      const ctx = document.getElementById('dashCollectionsChart');
      if (!ctx) return;

      if (appState.charts.collections) {
        appState.charts.collections.destroy();
      }

      // Real monthly collections derived from actual appState.payments
      const months = [];
      const dataPoints = [];
      const now = new Date();
      for (let i = 5; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        months.push(d.toLocaleString('default', { month: 'short' }));
        
        const sum = appState.payments
          .filter(p => {
            const dt = p.created_at || p.payment_date;
            if (!dt) return false;
            const pd = new Date(dt);
            return pd.getFullYear() === d.getFullYear() && pd.getMonth() === d.getMonth();
          })
          .reduce((total, p) => total + (Number(p.amount) || 0), 0);
        dataPoints.push(sum);
      }

      appState.charts.collections = new Chart(ctx, {
        type: 'line',
        data: {
          labels: months,
          datasets: [{
            label: 'Monthly Recoveries (PKR)',
            data: dataPoints,
            borderColor: '#ff6b35',
            backgroundColor: 'rgba(255, 107, 53, 0.12)',
            borderWidth: 3,
            fill: true,
            tension: 0.38,
            pointBackgroundColor: '#ff6b35',
            pointBorderColor: '#13131a',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` PKR ${(ctx.parsed.y || 0).toLocaleString()}`
              }
            }
          },
          scales: {
            x: {
              grid: { color: 'rgba(255,255,255,0.03)' },
              ticks: { color: '#a0a0b0', font: { size: 10 } }
            },
            y: {
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: {
                color: '#a0a0b0',
                font: { size: 10 },
                callback: (v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v
              },
              beginAtZero: true
            }
          }
        }
      });
    }'''

content = re.sub(
    r'function updateDashboardCounters\(\) \{[\s\S]*?function renderDashboardChart\(\) \{[\s\S]*?beginAtZero: true\s*\}\s*\}\s*\}\s*\}\);\s*\}',
    counters_replacement,
    content
)

# 7. Update openAddDeviceModal quota check
open_dev_modal_func = '''    function openAddDeviceModal() {
      const maxLimit = Number(appState.currentBusiness?.device_limit) || 250;
      const currentCount = appState.devices.length;
      if (currentCount >= maxLimit) {
        showToast(`Device limit reached (${currentCount} / ${maxLimit} slots used). Upgrade quota to enroll more devices.`, "error");
        return;
      }
      if (appState.customers.length === 0) {
        showToast("No customers registered yet. Please add a customer first.", "warning");
        openAddCustomerModal();
        return;
      }
      openModal('addDeviceModal');
      goToAddDevStep(1);
      populateCustomerSelectOptions();
    }'''

content = re.sub(
    r'function openAddDeviceModal\(\) \{[\s\S]*?populateCustomerSelectOptions\(\);\s*\}',
    open_dev_modal_func,
    content
)

# 8. Update handleSaveCustomer, handleSaveDeviceAndPlan, handleSavePayment
save_cust_func = '''    async function handleSaveCustomer(e) {
      if (e && e.preventDefault) e.preventDefault();
      const name = document.getElementById('newCustName').value.trim();
      const phone = document.getElementById('newCustPhone').value.trim();
      const cnic = document.getElementById('newCustCNIC').value.trim();
      const city = document.getElementById('newCustCity').value;
      const address = document.getElementById('newCustAddress').value.trim();
      const gName = document.getElementById('newCustGuarantorName').value.trim();
      const gPhone = document.getElementById('newCustGuarantorPhone').value.trim();
      const btn = document.getElementById('saveCustomerBtn');

      if (!name || !phone) {
        showToast("Please enter customer name and phone number", "error");
        return;
      }

      btn.disabled = true;
      btn.innerHTML = `<span class="gradient-spinner w-3.5 h-3.5 inline-block mr-2"></span> Saving...`;

      try {
        const newCustomer = {
          business_id: appState.currentBusinessId,
          name, phone, cnic, city, address,
          guarantor_name: gName,
          guarantor_phone: gPhone,
          status: 'active',
          created_at: new Date().toISOString()
        };

        const { data, error } = await sb.from('customers').insert(newCustomer).select();
        if (error) {
          console.error("[DB] Insert customer error:", error);
          throw error;
        }

        closeModal('addCustomerModal');
        document.getElementById('addCustomerForm').reset();
        
        // Refresh customer list directly from Supabase
        await loadRetailerData();

        showToast(`Customer ${name} registered successfully!`, "success");

      } catch (err) {
        console.error("Save customer error:", err);
        showToast(err.message || "Failed to save customer", "error");
      } finally {
        btn.disabled = false;
        btn.innerText = "Save Customer";
      }
    }'''

content = re.sub(
    r'async function handleSaveCustomer\(e\) \{[\s\S]*?btn\.innerText = "Save Customer";\s*\}\s*\}',
    save_cust_func,
    content
)

save_dev_func = '''    async function handleSaveDeviceAndPlan() {
      const sel = document.getElementById('newDevCustomerSelect');
      const custId = sel.value;
      const custName = sel.options[sel.selectedIndex]?.text;
      const model = document.getElementById('newDevModel').value.trim();
      const imei = document.getElementById('newDevIMEI1').value.trim();
      const imei2 = document.getElementById('newDevIMEI2').value.trim();
      const total = Number(document.getElementById('newDevTotalPrice').value) || 0;
      const down = Number(document.getElementById('newDevDownPayment').value) || 0;
      const tenure = Number(document.getElementById('newDevTenure').value) || 12;
      const dueDay = Number(document.getElementById('newDevDueDay').value) || 5;
      const monthly = Math.round((total - down) / tenure);
      const btn = document.getElementById('saveDeviceBtn');

      const maxLimit = Number(appState.currentBusiness?.device_limit) || 250;
      if (appState.devices.length >= maxLimit) {
        showToast(`Device limit reached (${appState.devices.length} / ${maxLimit} slots used). Cannot enroll more devices.`, "error");
        return;
      }

      if (!custId || !model || !imei) {
        showToast("Please fill all required device details", "error");
        return;
      }

      btn.disabled = true;
      btn.innerHTML = `<span class="gradient-spinner w-3.5 h-3.5 inline-block mr-2"></span> Activating...`;

      try {
        const newDev = {
          business_id: appState.currentBusinessId,
          customer_id: custId,
          customer_name: custName,
          model, imei, imei_2: imei2,
          purchase_price: total,
          is_locked: false,
          status: 'active',
          battery: 100,
          sim_carrier: 'Jazz 4G',
          emi_paid: 1,
          emi_total: tenure,
          last_seen: 'Just Now',
          created_at: new Date().toISOString()
        };

        const { data: devData, error: devErr } = await sb.from('devices').insert(newDev).select();
        if (devErr) {
          console.error("[DB] Insert device error:", devErr);
          throw devErr;
        }

        const createdDevId = (devData && devData[0]) ? devData[0].id : `dev-${Date.now()}`;

        // Insert EMI Plan into emi_plans table
        const newPlan = {
          business_id: appState.currentBusinessId,
          customer_id: custId,
          device_id: createdDevId,
          total_amount: total,
          down_payment: down,
          monthly_installment: monthly,
          monthly_amount: monthly,
          duration_months: tenure,
          tenure_months: tenure,
          paid_months: 1,
          paid_amount: down,
          total_paid: down,
          remaining_amount: Math.max(0, total - down),
          due_day: dueDay,
          status: 'active',
          created_at: new Date().toISOString()
        };

        const { error: planErr } = await sb.from('emi_plans').insert(newPlan);
        if (planErr) {
          console.warn("[DB] Insert emi_plan notice:", planErr);
        }

        closeModal('addDeviceModal');
        goToAddDevStep(1);
        document.getElementById('addDeviceForm').reset();
        
        // Refresh from Supabase
        await loadRetailerData();

        showToast(`${model} enrolled on installment plan!`, "success");

      } catch (err) {
        console.error("Save device error:", err);
        showToast(err.message || "Failed to enroll device", "error");
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i> Complete & Activate Device`;
        lucide.createIcons();
      }
    }'''

content = re.sub(
    r'async function handleSaveDeviceAndPlan\(\) \{[\s\S]*?btn\.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i> Complete & Activate Device`;\s*\}\s*\}',
    save_dev_func,
    content
)

save_pay_func = '''    async function handleSavePayment(e) {
      if (e && e.preventDefault) e.preventDefault();
      const select = document.getElementById('payDeviceSelect');
      const amount = Number(document.getElementById('payAmount').value);
      const channel = document.getElementById('payChannel').value;
      const trxId = document.getElementById('payTrxId').value.trim() || `TRX-${Date.now().toString().slice(-6)}`;
      const btn = document.getElementById('savePaymentBtn');

      if (!select.value || !amount) {
        showToast("Please select a customer device and enter amount", "error");
        return;
      }

      btn.disabled = true;
      btn.innerHTML = `<span class="gradient-spinner w-3.5 h-3.5 inline-block mr-2"></span> Recording...`;

      try {
        const [devId, custId, custName] = select.value.split('|');

        const newPayment = {
          business_id: appState.currentBusinessId,
          customer_id: custId,
          device_id: devId,
          customer_name: custName,
          amount: amount,
          channel: channel,
          payment_method: channel,
          transaction_id: trxId,
          status: 'completed',
          created_at: new Date().toISOString()
        };

        const { error: payErr } = await sb.from('payments').insert(newPayment);
        if (payErr) {
          console.error("[DB] Insert payment error:", payErr);
          throw payErr;
        }

        // UPDATE emi_plans total_paid, remaining_amount
        const plan = appState.emiPlans.find(p => p.device_id === devId);
        if (plan) {
          const newPaid = (Number(plan.total_paid || plan.paid_amount) || 0) + amount;
          const newRem = Math.max(0, (Number(plan.total_amount) || 0) - newPaid);
          const newMonths = (Number(plan.paid_months) || 0) + 1;
          await sb.from('emi_plans').update({
            total_paid: newPaid,
            paid_amount: newPaid,
            remaining_amount: newRem,
            paid_months: newMonths
          }).eq('device_id', devId);
        }

        // Also unlock device if it was locked
        const dev = appState.devices.find(d => d.id === devId);
        if (dev && dev.is_locked) {
          await sb.from('devices').update({ is_locked: false, status: 'active' }).eq('id', devId);
        }

        closeModal('recordPaymentModal');
        document.getElementById('recordPaymentForm').reset();
        
        // Refresh UI from real Supabase data
        await loadRetailerData();

        // Trigger Confetti Celebration!
        if (window.confetti) {
          window.confetti({
            particleCount: 80,
            spread: 70,
            origin: { y: 0.6 }
          });
        }

        showToast(`Payment of PKR ${amount.toLocaleString()} recorded successfully!`, "success");

      } catch (err) {
        console.error("Save payment error:", err);
        showToast(err.message || "Failed to record payment", "error");
      } finally {
        btn.disabled = false;
        btn.innerText = "Record Payment";
      }
    }'''

content = re.sub(
    r'async function handleSavePayment\(e\) \{[\s\S]*?btn\.disabled = false;\s*\}\s*\}',
    save_pay_func,
    content
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('app/applet/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Pass 2 completed successfully!")
