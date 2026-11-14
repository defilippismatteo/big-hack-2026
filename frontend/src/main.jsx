import React, { useEffect, useRef, useSyncExternalStore } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowLeft, CalendarDays, ChevronRight, Compass, Menu, X,
} from 'lucide-react';
import '@fontsource-variable/inter';
import { getSection, groups, sectionHref, sections } from './sections';
import './styles.css';
import { Overview } from './overview/Overview';
import { AudienceLab } from './pages/AudienceLab';
import { CreativeExplorer } from './creatives/CreativeExplorer';

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

  const Page = { overview: Overview, creatives: CreativeExplorer, audience: AudienceLab }[current.id] ?? SectionLanding;

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
          <Page section={current} headingRef={heading} />
        </main>
        <footer className="footer">
          <span>Developed for Wevion · The Big Hack 2026</span>
          <span className="preview-label">Anteprima ADERA</span>
        </footer>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
