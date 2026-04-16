(function(){
  const menuBtn = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#mainNav');
  if(menuBtn && nav){menuBtn.addEventListener('click',()=>{const open=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',String(open));});}
  document.querySelectorAll('a[href^="#"]').forEach(link=>{link.addEventListener('click',(e)=>{const id=link.getAttribute('href');if(!id||id==='#')return;const target=document.querySelector(id);if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth',block:'start'});}});});
  document.querySelectorAll('.faq-question').forEach(btn=>btn.addEventListener('click',()=>{const item=btn.closest('.faq-item');if(item)item.classList.toggle('open');}));
  const form=document.querySelector('#contactForm');
  if(form){form.addEventListener('submit',(e)=>{e.preventDefault();const nome=form.querySelector('[name="nome"]');const tel=form.querySelector('[name="telefone"]');const bairro=form.querySelector('[name="bairro"]');const servico=form.querySelector('[name="servico"]');const msg=form.querySelector('[name="mensagem"]');const notice=form.querySelector('.notice');const errors=[];
  if(!nome.value.trim())errors.push('Informe seu nome.');
  if(!/^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$/.test(tel.value.replace(/\s+/g,'')))errors.push('Informe um telefone válido com DDD.');
  if(!bairro.value)errors.push('Selecione um bairro.');if(!servico.value)errors.push('Selecione um serviço.');if(msg.value.trim().length<10)errors.push('Descreva sua necessidade com pelo menos 10 caracteres.');
  if(errors.length){notice.textContent=errors[0];return;}notice.style.color='#166534';notice.textContent='Mensagem validada com sucesso. Nossa equipe retornará em breve.';form.reset();});}
})();
