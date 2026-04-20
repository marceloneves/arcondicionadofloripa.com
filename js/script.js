(function(){
  function formatPhoneBR(value){
    const digits = value.replace(/\D/g,'').slice(0,11);
    if(digits.length<=2)return digits;
    if(digits.length<=6)return `(${digits.slice(0,2)}) ${digits.slice(2)}`;
    if(digits.length<=10)return `(${digits.slice(0,2)}) ${digits.slice(2,6)}-${digits.slice(6)}`;
    return `(${digits.slice(0,2)}) ${digits.slice(2,7)}-${digits.slice(7)}`;
  }

  const menuBtn = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#mainNav');
  if(menuBtn && nav){menuBtn.addEventListener('click',()=>{const open=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',String(open));});}
  document.querySelectorAll('a[href^="#"]').forEach(link=>{link.addEventListener('click',(e)=>{const id=link.getAttribute('href');if(!id||id==='#')return;const target=document.querySelector(id);if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth',block:'start'});}});});
  document.querySelectorAll('.faq-question').forEach(btn=>btn.addEventListener('click',()=>{const item=btn.closest('.faq-item');if(item)item.classList.toggle('open');}));
  const form=document.querySelector('#contactForm');
  if(form){const tel=form.querySelector('[name="telefone"]');if(tel){tel.addEventListener('input',()=>{tel.value=formatPhoneBR(tel.value);});}form.addEventListener('submit',async (e)=>{e.preventDefault();const nome=form.querySelector('[name="nome"]');const email=form.querySelector('[name="email"]');const cidade=form.querySelector('[name="cidade"]');const servico=form.querySelector('[name="servico"]');const msg=form.querySelector('[name="mensagem"]');const notice=form.querySelector('.notice');const submitBtn=form.querySelector('button[type="submit"]');const errors=[];
  if(!nome.value.trim())errors.push('Informe seu nome.');
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))errors.push('Informe um e-mail válido.');
  if(!/^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$/.test(tel.value.replace(/\s+/g,'')))errors.push('Informe um telefone válido com DDD.');
  if(!cidade.value)errors.push('Selecione uma cidade.');if(!servico.value)errors.push('Selecione um serviço.');if(msg.value.trim().length<10)errors.push('Descreva sua necessidade com pelo menos 10 caracteres.');
  if(errors.length){notice.style.color='#b91c1c';notice.textContent=errors[0];return;}
  if(submitBtn){submitBtn.disabled=true;}
  notice.style.color='#374151';notice.textContent='Enviando mensagem...';
  try{
    const response=await fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome:nome.value.trim(),email:email.value.trim(),telefone:tel.value.trim(),cidade:cidade.value,servico:servico.value,mensagem:msg.value.trim()})});
    const data=await response.json().catch(()=>({}));
    if(!response.ok){
      const debugMissing = data && data.missing ? ` (missing: apiKey=${String(data.missing.resendApiKey)}, fromEmail=${String(data.missing.resendFromEmail)})` : '';
      const debugDetails = data && data.details ? ` Detalhe: ${String(data.details)}` : '';
      throw new Error((data.error||'Falha ao enviar mensagem.')+debugMissing+debugDetails);
    }
    notice.style.color='#166534';notice.textContent='Mensagem enviada com sucesso. Nossa equipe retornará em breve.';form.reset();
  }catch(err){
    notice.style.color='#b91c1c';notice.textContent=err.message||'Não foi possível enviar. Tente novamente em instantes.';
  }finally{
    if(submitBtn){submitBtn.disabled=false;}
  }});}

  const galleryLinks = document.querySelectorAll('.home-instalacao-link');
  if(galleryLinks.length){
    const lightbox = document.createElement('div');
    lightbox.className = 'img-lightbox';
    lightbox.innerHTML = '<button class="img-lightbox-close" type="button" aria-label="Fechar imagem">Fechar</button><img alt="">';
    document.body.appendChild(lightbox);
    const lbImg = lightbox.querySelector('img');
    const closeBtn = lightbox.querySelector('.img-lightbox-close');
    const close = ()=>lightbox.classList.remove('open');

    galleryLinks.forEach(link=>{
      link.addEventListener('click',(e)=>{
        e.preventDefault();
        const img = link.querySelector('img');
        lbImg.src = link.getAttribute('href');
        lbImg.alt = img ? img.alt : 'Imagem ampliada';
        lightbox.classList.add('open');
      });
    });

    closeBtn.addEventListener('click', close);
    lightbox.addEventListener('click',(e)=>{ if(e.target === lightbox) close(); });
    document.addEventListener('keydown',(e)=>{ if(e.key === 'Escape') close(); });
  }
})();
