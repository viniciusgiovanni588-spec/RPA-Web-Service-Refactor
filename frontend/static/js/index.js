/**
 * Classe responsável por controlar o menu mobile da navegação.
 * 
 * Realiza:
 * - abertura e fechamento do menu mobile
 * - animação dos links de navegação
 * adição e remoção de classes CSS dinamicamente
 * 
 * A clsse utiliza manipulação de DOM para adicionar
 * interatividade ao menu responsivo.
 */

class MobileNavbar {
    /**
     * Cria uma instância do menu mobile.
     * 
     * @param {string} mobileMenu - Seletor CSS do botão/menu mobile.
     * @param {string} navList - Seletor CSS da lista de navegação.
     * @param {String} navLinks - Seletor CSS dos links de navegação.
     */

    constructor(mobileMenu, navList, navLinks) {
        this.mobileMenu = document.querySelector(mobileMenu);
        this.navList = document.querySelector(navList);
        this.navLinks = document.querySelectorAll(navLinks);
        this.activeClass = "active";

        this.handleClick = this.handleClick.bind(this);
    }

    animateLinks() {
        this.navLinks.forEach((link, index) => {
            link.style.animation
                ? (link.style.animation = "")
                : (link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`);
        });
    }

    handleClick() {
        this.navList.classList.toggle(this.activeClass);
        this.mobileMenu.classList.toggle(this.activeClass);
        this.animateLinks();
    }

    addClickEvent() {
        this.mobileMenu.addEventListener("click", this.handleClick);
    }

    init() {
        if (this.mobileMenu) {
            this.addClickEvent();
        }
        return this;
    }
}

const mobileNavbar = new MobileNavbar(
    ".mobile-menu",
    ".nav-list",
    ".nav-list li",
);
mobileNavbar.init();