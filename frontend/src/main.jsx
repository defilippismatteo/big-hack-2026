import React, { useEffect, useRef, useSyncExternalStore } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowDown, ArrowLeft, ArrowUpRight, CalendarDays, ChevronRight, Compass, Menu, X,
} from 'lucide-react';
import '@fontsource-variable/inter';
import { getSection, groups, sectionHref, sections } from './sections';
import './styles.css';

const logo = import.meta.env.BASE_URL + 'adera.svg';

function subscribeRoute(listener) {
  window.addEventListener('hashchange', listener);
  return () => window.removeEventListener('hashchange', listener);
}

function Brand() {
  return (
    <a className="brand" href={sectionHref('overview')} aria-label="ADERA, Overview">
      <img src={logo} width="44" height="44" alt="" />
      <span className="brand-text">
        <strong>ADERA</strong>
        <span>Audience &amp; Advertising<br />Intelligence</span>
      </span>
    </a>
  );
}

function Sidebar({ current, onNavigate }) {
  return (
    <div className="sidebar-inner">
      <div onClick={onNavigate}><Brand /></div>
      <nav aria-label="Navigazione principale" onClick={onNavigate}>
        {groups.map((group) => (
          <div className="nav-group" key={group}>
            <p className="nav-title">{group}</p>
            <ul>
              {sections.filter((section) => section.group === group).map(({ id, label, icon: Icon }) => (
                <li key={id}>
                  <a href={sectionHref(id)} aria-current={current.id === id ? 'page' : undefined}>
                    <Icon aria-hidden="true" size={18} strokeWidth={1.8} />
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      <div className="project-note">
        <span className="project-mark" aria-hidden="true">W</span>
        <span><strong>Challenge Wevion</strong><small>The Big Hack 2026</small></span>
      </div>
    </div>
  );
}

function Header({ current, onMenu, menuOpen }) {
  return (
    <header className="topbar">
      <button className="icon-button menu-button" type="button" aria-label="Apri navigazione"
        aria-expanded={menuOpen} aria-controls="mobile-navigation" onClick={onMenu}>
        <Menu size={21} aria-hidden="true" />
      </button>
      <div className="breadcrumbs">
        <span>{current.group}</span>
        <ChevronRight size={14} aria-hidden="true" />
        <strong>{current.label}</strong>
      </div>
      <div className="period" aria-label="Periodo di previsione: 16–30 novembre 2026">
        <CalendarDays size={16} aria-hidden="true" />
        <span className="period-full">16–30 novembre 2026</span>
        <span className="period-short" aria-hidden="true">16–30 nov</span>
      </div>
    </header>
  );
}

function Radar() {
  return (
    <svg className="radar" viewBox="0 0 420 300" aria-hidden="true">
      <defs>
        <pattern id="radar-grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" stroke="#9b82e8" strokeWidth=".8" fill="none" />
        </pattern>
        <radialGradient id="radar-fade">
          <stop offset="0" stopColor="white" />
          <stop offset="1" stopColor="white" stopOpacity="0" />
        </radialGradient>
        <mask id="radar-mask"><ellipse cx="225" cy="150" rx="195" ry="150" fill="url(#radar-fade)" /></mask>
        <linearGradient id="radar-a" x2="1" y2="1">
          <stop stopColor="#9d87e7" /><stop offset="1" stopColor="#6041be" />
        </linearGradient>
      </defs>
      <rect width="420" height="300" fill="url(#radar-grid)" mask="url(#radar-mask)" opacity=".55" />
      <g fill="none" stroke="#8465d7">
        <circle cx="233" cy="148" r="113" opacity=".26" strokeDasharray="4 6" />
        <circle cx="233" cy="148" r="86" opacity=".35" />
        <circle cx="233" cy="148" r="58" opacity=".25" />
        <ellipse cx="233" cy="148" rx="146" ry="60" transform="rotate(-24 233 148)" opacity=".52" />
        <path d="M124 203 343 94M233 21v254" opacity=".20" />
      </g>
      <circle cx="136" cy="192" r="5" fill="#a089ed" />
      <circle cx="315" cy="80" r="5" fill="#8062e3" />
      <circle cx="315" cy="80" r="10" fill="none" stroke="#8062e3" opacity=".42" />
      <circle cx="260" cy="229" r="4" fill="#8062e3" />
      <path d="M193 182 226 114a7 7 0 0 1 13 0l33 68m-63-17h47" fill="none" stroke="url(#radar-a)" strokeWidth="7" strokeLinecap="round" />
      <path d="M267 112v21m-10.5-10.5h21" fill="none" stroke="#8062e3" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

function Overview({ headingRef }) {
  function explore() {
    const moduleHeading = document.getElementById('modules-title');
    moduleHeading.focus();
  }

  return (
    <>
      <section className="hero" aria-labelledby="page-title">
        <div className="hero-content">
          <span className="hero-label"><span aria-hidden="true" /> BLACK FRIDAY 2026</span>
          <h1 id="page-title" ref={headingRef} tabIndex={-1}>Decidi prima<br />di spendere.</h1>
          <p>Esplora il pubblico, confronta gli annunci e valuta come distribuire il budget per il Black Friday.</p>
          <button className="primary-button" type="button" onClick={explore}>
            Esplora le sezioni <ArrowDown size={16} aria-hidden="true" />
          </button>
        </div>
        <Radar />
      </section>

      <section className="modules" aria-labelledby="modules-title">
        <div className="modules-intro">
          <h2 id="modules-title" tabIndex={-1}>Esplora ADERA</h2>
          <p>Cinque sezioni per orientare le decisioni sulle campagne.</p>
        </div>
        <div className="module-grid">
          {sections.slice(1).map(({ id, icon: Icon, label, description, tone }) => (
            <a className="module-card" key={id} href={sectionHref(id)}>
              <div className="module-top">
                <span className={'module-icon ' + tone}><Icon size={20} strokeWidth={1.8} aria-hidden="true" /></span>
                <ArrowUpRight className="module-arrow" size={18} aria-hidden="true" />
              </div>
              <h3>{label}</h3>
              <p>{description}</p>
            </a>
          ))}
        </div>
      </section>
    </>
  );
}

function SectionLanding({ section, headingRef }) {
  const Icon = section.icon;
  return (
    <section className="section-landing" aria-labelledby="page-title">
      <a className="back-link" href={sectionHref('overview')}><ArrowLeft size={16} aria-hidden="true" /> Overview</a>
      <div className="section-title">
        <span className={'module-icon ' + section.tone}><Icon size={23} aria-hidden="true" /></span>
        <div>
          <h1 id="page-title" ref={headingRef} tabIndex={-1}>{section.label}</h1>
          <p>{section.description}</p>
        </div>
      </div>
      <div className="empty-state">
        <Compass size={26} strokeWidth={1.7} aria-hidden="true" />
        <h2>Sezione in preparazione</h2>
        <p>Questa anteprima include la navigazione. I dati e gli strumenti di questa sezione saranno disponibili in un prossimo aggiornamento.</p>
      </div>
    </section>
  );
}

function App() {
  const current = useSyncExternalStore(subscribeRoute, getSection);
  const dialog = useRef(null);
  const heading = useRef(null);
  const previousSection = useRef(current.id);
  const [menuOpen, setMenuOpen] = React.useState(false);

  useEffect(() => {
    document.title = current.label + ' · ADERA';
    if (previousSection.current !== current.id) {
      previousSection.current = current.id;
      window.scrollTo(0, 0);
      heading.current?.focus({ preventScroll: true });
    }
  }, [current]);

  useEffect(() => {
    const wideScreen = window.matchMedia('(min-width: 901px)');
    function onResize(event) {
      if (event.matches) dialog.current?.close();
    }
    wideScreen.addEventListener('change', onResize);
    return () => wideScreen.removeEventListener('change', onResize);
  }, []);

  function openMenu() {
    if (!dialog.current.open) {
      dialog.current.showModal();
      setMenuOpen(true);
    }
  }

  function navigateFromMenu(event) {
    if (event.target.closest('a') && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) {
      dialog.current.close();
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content" onClick={(event) => {
        event.preventDefault();
        document.getElementById('main-content').focus();
      }}>Vai al contenuto</a>
      <aside className="desktop-sidebar"><Sidebar current={current} /></aside>
      <dialog id="mobile-navigation" className="mobile-sidebar" ref={dialog}
        aria-label="Menu ADERA" onClose={() => setMenuOpen(false)}
        onClick={(event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }}>
        <button type="button" className="icon-button close-button" aria-label="Chiudi navigazione"
          onClick={() => dialog.current.close()}>
          <X size={21} aria-hidden="true" />
        </button>
        <Sidebar current={current} onNavigate={navigateFromMenu} />
      </dialog>
      <div className="workspace">
        <Header current={current} onMenu={openMenu} menuOpen={menuOpen} />
        <main className="main" id="main-content" tabIndex={-1}>
          {current.id === 'overview'
            ? <Overview headingRef={heading} />
            : <SectionLanding section={current} headingRef={heading} />}
        </main>
        <footer className="footer">
          <span>Developed for Wevion · The Big Hack 2026</span>
          <span className="preview-label">Anteprima design</span>
        </footer>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
